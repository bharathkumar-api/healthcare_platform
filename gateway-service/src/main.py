from fastapi import FastAPI, Request, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import httpx
import os

app = FastAPI(title="API Gateway")

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
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8004")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway"}

async def proxy_request(request: Request, target_url: str, authorization: Optional[str] = None):
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {}
        
        # Copy all headers except host and content-length
        for key, value in request.headers.items():
            if key.lower() not in ['host', 'content-length']:
                headers[key] = value
        
        # Ensure Authorization header is present
        if authorization and 'authorization' not in headers:
            headers['authorization'] = authorization
        
        print(f"[GATEWAY] Proxying {request.method} to: {target_url}")
        print(f"[GATEWAY] Authorization header present: {'authorization' in headers}")
        
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
            params=request.query_params
        )
        
        print(f"[GATEWAY] Response status: {response.status_code}")
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def auth_proxy(request: Request, path: str, authorization: Optional[str] = Header(None)):
    target_url = f"{AUTH_SERVICE_URL}/api/v1/auth/{path}"
    return await proxy_request(request, target_url, authorization)

@app.api_route("/api/v1/appointments/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
@app.api_route("/api/v1/appointments", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def appointments_proxy(request: Request, authorization: Optional[str] = Header(None), path: str = ""):
    if path:
        target_url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/{path}"
    else:
        target_url = f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/"
    return await proxy_request(request, target_url, authorization)

@app.api_route("/api/v1/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def notifications_proxy(request: Request, path: str, authorization: Optional[str] = Header(None)):
    target_url = f"{NOTIFICATION_SERVICE_URL}/api/v1/notifications/{path}"
    return await proxy_request(request, target_url, authorization)
