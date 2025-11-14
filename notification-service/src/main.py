from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
import logging
import time
from uuid import uuid4
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
SERVICE_NAME = "notification-service"
logger = logging.getLogger(SERVICE_NAME)

app = FastAPI(title="Notification Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Consistency layer for HTTP logging (WebSockets handled separately)."""
    start = time.perf_counter()
    correlation_id = request.headers.get("x-correlation-id", str(uuid4()))
    request.state.correlation_id = correlation_id

    try:
        response = await call_next(request)
    except Exception as exc:
        duration = (time.perf_counter() - start) * 1000
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": SERVICE_NAME,
            "method": request.method,
            "path": request.url.path,
            "status": 500,
            "duration_ms": round(duration, 2),
            "correlation_id": correlation_id,
            "error": str(exc)
        }
        logger.exception(json.dumps(error_entry))
        raise

    duration = (time.perf_counter() - start) * 1000
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": SERVICE_NAME,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round(duration, 2),
        "correlation_id": correlation_id
    }

    if response.status_code >= 500:
        logger.error(json.dumps(log_entry))
    elif response.status_code >= 400:
        logger.warning(json.dumps(log_entry))
    else:
        logger.info(json.dumps(log_entry))

    response.headers["X-Correlation-ID"] = correlation_id
    return response

# Store active WebSocket connections
active_connections: Dict[int, List[WebSocket]] = {}

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST", "mailhog")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@healthcare.com")

class PushNotification(BaseModel):
    user_id: int
    type: str
    title: str
    message: str
    data: Optional[dict] = {}

class EmailNotification(BaseModel):
    to_email: str
    subject: str
    body: str
    html_body: Optional[str] = None

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "notification",
        "active_connections": sum(len(conns) for conns in active_connections.values()),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for user {user_id}")
    
    # Add connection to active connections
    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(websocket)
    
    logger.info(f"Active connections for user {user_id}: {len(active_connections[user_id])}")
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "connection",
            "title": "Connected",
            "message": "Real-time notifications enabled",
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_json(welcome_msg)
        
        # Keep connection alive
        while True:
            # Wait for any message from client (heartbeat)
            data = await websocket.receive_text()
            logger.debug(f"Received from user {user_id}: {data}")
            
            # Echo back or send ack
            await websocket.send_json({
                "type": "ack",
                "message": "Message received",
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
    finally:
        # Remove connection
        if user_id in active_connections:
            if websocket in active_connections[user_id]:
                active_connections[user_id].remove(websocket)
            if not active_connections[user_id]:
                del active_connections[user_id]
        logger.info(f"Cleaned up connection for user {user_id}")

@app.post("/api/v1/notifications/push")
async def send_push_notification(
    notification: PushNotification,
    x_user_id: Optional[str] = Header(None),
    x_correlation_id: Optional[str] = Header(None)
):
    """Send push notification to user via WebSocket"""
    try:
        logger.info(f"Push notification request for user {notification.user_id}: {notification.title}")
        
        user_id = notification.user_id
        
        # Check if user has active connections
        if user_id not in active_connections or not active_connections[user_id]:
            logger.warning(f"No active connections for user {user_id}")
            return {
                "status": "no_connections",
                "message": f"User {user_id} has no active WebSocket connections",
                "user_id": user_id
            }
        
        # Prepare notification payload
        notification_data = {
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "data": notification.data,
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": x_correlation_id
        }
        
        # Send to all active connections for this user
        disconnected = []
        sent_count = 0
        
        for websocket in active_connections[user_id]:
            try:
                await websocket.send_json(notification_data)
                sent_count += 1
                logger.info(f"Notification sent to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send to connection: {str(e)}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            active_connections[user_id].remove(ws)
        
        if not active_connections[user_id]:
            del active_connections[user_id]
        
        return {
            "status": "sent",
            "message": f"Notification sent to {sent_count} connection(s)",
            "user_id": user_id,
            "connections_count": sent_count,
            "notification": notification_data
        }
        
    except Exception as e:
        logger.error(f"Error sending push notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/notifications/email")
async def send_email_notification(
    email: EmailNotification,
    x_correlation_id: Optional[str] = Header(None)
):
    """Send email notification"""
    try:
        logger.info(f"Sending email to {email.to_email}: {email.subject}")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = email.subject
        msg['From'] = FROM_EMAIL
        msg['To'] = email.to_email
        msg['X-Correlation-ID'] = x_correlation_id or "no-correlation-id"
        
        # Plain text
        text_part = MIMEText(email.body, 'plain')
        msg.attach(text_part)
        
        # HTML if provided
        if email.html_body:
            html_part = MIMEText(email.html_body, 'html')
            msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {email.to_email}")
        
        return {
            "status": "sent",
            "message": f"Email sent to {email.to_email}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@app.get("/api/v1/notifications/connections")
async def get_active_connections():
    """Get active WebSocket connections"""
    connections_summary = {
        user_id: len(connections) 
        for user_id, connections in active_connections.items()
    }
    
    return {
        "active_users": len(active_connections),
        "total_connections": sum(len(conns) for conns in active_connections.values()),
        "connections_by_user": connections_summary
    }

@app.get("/")
async def root():
    return {
        "service": "notification",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "websocket": "/ws/{user_id}",
            "push": "/api/v1/notifications/push",
            "email": "/api/v1/notifications/email",
            "connections": "/api/v1/notifications/connections"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
