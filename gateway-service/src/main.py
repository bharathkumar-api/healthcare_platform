from fastapi import FastAPI, Request, Response, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import httpx
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from jose import JWTError, jwt
import logging
import json
import asyncio

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Healthcare API Gateway", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
APPOINTMENT_SERVICE_URL = os.getenv("APPOINTMENT_SERVICE_URL", "http://appointment-service:8003")
PATIENT_SERVICE_URL = os.getenv("PATIENT_SERVICE_URL", "http://patient-service:8005")
PROVIDER_SERVICE_URL = os.getenv("PROVIDER_SERVICE_URL", "http://provider-service:8006")
BILLING_SERVICE_URL = os.getenv("BILLING_SERVICE_URL", "http://billing-service:8007")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8004")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production-12345")
ALGORITHM = "HS256"

rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

SERVICE_ROUTES = {
    "auth": AUTH_SERVICE_URL,
    "appointments": APPOINTMENT_SERVICE_URL,
    "patients": PATIENT_SERVICE_URL,
    "providers": PROVIDER_SERVICE_URL,
    "billing": BILLING_SERVICE_URL,
    "notifications": NOTIFICATION_SERVICE_URL,
}

PUBLIC_ENDPOINTS = [
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/health",
    "/api/health",
    "/docs",
    "/openapi.json"
]

def log_request(correlation_id: str, method: str, path: str, status: int, duration: float, user_id: Optional[str] = None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "correlation_id": correlation_id,
        "service": "gateway",
        "method": method,
        "path": path,
        "status": status,
        "duration_ms": round(duration * 1000, 2),
        "user_id": user_id
    }
    logger.info(json.dumps(log_entry))

def check_rate_limit(client_ip: str) -> bool:
    now = datetime.now()
    cutoff = now - timedelta(seconds=RATE_LIMIT_WINDOW)
    rate_limit_store[client_ip] = [req_time for req_time in rate_limit_store[client_ip] if req_time > cutoff]
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    rate_limit_store[client_ip].append(now)
    return True

def verify_token(token: str) -> Optional[dict]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("sub"),
            "role": payload.get("role")
        }
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        return None

def is_authorized(user: dict, path: str, method: str) -> bool:
    role = user.get("role", "").lower()
    
    # Admin has access to everything
    if role == "admin":
        return True
    
    # Allow all authenticated users to access notifications
    if path.startswith("/api/v1/notifications"):
        return True
    
    # Allow all authenticated users to access providers (read-only)
    if path.startswith("/api/v1/providers") and method == "GET":
        return True
    
    # Doctor permissions
    if role == "doctor":
        if path.startswith("/api/v1/appointments") or path.startswith("/api/v1/patients") or path.startswith("/api/v1/providers"):
            return True
    
    # Patient permissions
    if role == "patient":
        if path.startswith("/api/v1/appointments") or path.startswith("/api/v1/patients") or path.startswith("/api/v1/billing"):
            return True
    
    # Allow users to access their own auth endpoints
    if path.startswith("/api/v1/auth/me") or path.startswith("/api/v1/auth/logout"):
        return True
    
    return False

@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    start_time = time.time()
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["X-Correlation-ID"] = correlation_id
        return response
    
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        duration = time.time() - start_time
        log_request(correlation_id, request.method, request.url.path, 429, duration)
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={"X-Correlation-ID": correlation_id}
        )
    
    is_public = any(request.url.path.startswith(endpoint) for endpoint in PUBLIC_ENDPOINTS)
    
    user_id = None
    if not is_public:
        authorization = request.headers.get("authorization")
        user = verify_token(authorization.replace("Bearer ", "") if authorization else "")
        
        if not user:
            duration = time.time() - start_time
            log_request(correlation_id, request.method, request.url.path, 401, duration)
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing authentication token"},
                headers={"X-Correlation-ID": correlation_id}
            )
        
        user_id = user.get("user_id")
        
        if not is_authorized(user, request.url.path, request.method):
            duration = time.time() - start_time
            log_request(correlation_id, request.method, request.url.path, 403, duration, user_id)
            return JSONResponse(
                status_code=403,
                content={"detail": "Access forbidden: insufficient permissions"},
                headers={"X-Correlation-ID": correlation_id}
            )
        
        request.state.user = user
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    
    duration = time.time() - start_time
    log_request(correlation_id, request.method, request.url.path, response.status_code, duration, user_id)
    
    return response

async def proxy_request(request: Request, target_url: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {}
        for key, value in request.headers.items():
            if key.lower() not in ['host', 'content-length']:
                headers[key] = value
        
        headers['X-Correlation-ID'] = request.state.correlation_id
        
        if hasattr(request.state, 'user'):
            headers['X-User-ID'] = str(request.state.user.get('user_id'))
            headers['X-User-Role'] = request.state.user.get('role', '')
        
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=await request.body(),
                params=request.query_params
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Gateway timeout")
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise HTTPException(status_code=502, detail="Bad gateway")

@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, token: Optional[str] = None):
    """Direct WebSocket connection to notification service"""
    
    if token:
        user = verify_token(token)
        if not user or user.get("user_id") != user_id:
            await websocket.close(code=1008, reason="Unauthorized")
            logger.warning(f"WebSocket auth failed for user {user_id}")
            return
    else:
        logger.warning(f"No token provided for WebSocket connection user {user_id}")
        await websocket.close(code=1008, reason="Token required")
        return
    
    await websocket.accept()
    logger.info(f"WebSocket accepted for user {user_id}")
    
    notification_ws_url = NOTIFICATION_SERVICE_URL.replace("http://", "ws://") + f"/ws/{user_id}"
    
    try:
        import websockets
        async with websockets.connect(notification_ws_url) as notification_ws:
            logger.info(f"Connected to notification service for user {user_id}")
            
            async def receive_from_notification():
                try:
                    async for message in notification_ws:
                        await websocket.send_text(message)
                        logger.debug(f"Forwarded message to user {user_id}")
                except Exception as e:
                    logger.error(f"Error receiving from notification service: {str(e)}")
            
            async def receive_from_client():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await notification_ws.send(data)
                        logger.debug(f"Forwarded message from user {user_id}")
                except WebSocketDisconnect:
                    logger.info(f"Client {user_id} disconnected")
                except Exception as e:
                    logger.error(f"Error receiving from client: {str(e)}")
            
            await asyncio.gather(
                receive_from_notification(),
                receive_from_client()
            )
    
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        try:
            await websocket.close(code=1011, reason="Internal error")
        except:
            pass

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway", "version": "2.0.0"}

@app.get("/api/health")
async def api_health():
    services_health = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_url in SERVICE_ROUTES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=2.0)
                services_health[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2)
                }
            except Exception as e:
                services_health[service_name] = {"status": "unreachable", "error": str(e)}
    
    all_healthy = all(s["status"] == "healthy" for s in services_health.values())
    return {"status": "healthy" if all_healthy else "degraded", "gateway": "healthy", "services": services_health}

@app.api_route("/api/v1/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def route_service(request: Request, service: str, path: str = ""):
    service_url = SERVICE_ROUTES.get(service)
    if not service_url:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    if path:
        target_url = f"{service_url}/api/v1/{service}/{path}"
    else:
        target_url = f"{service_url}/api/v1/{service}/"
    
    return await proxy_request(request, target_url)
