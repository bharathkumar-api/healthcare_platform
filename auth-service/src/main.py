from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import logging
import json
import time
from uuid import uuid4
from datetime import datetime as dt

from .database import engine, Base, get_db
from .models import User
from .schemas import UserCreate, UserResponse, Token
from .core.security import get_password_hash, verify_password, create_access_token

SERVICE_NAME = "auth-service"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(SERVICE_NAME)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Emit structured JSON logs with correlation IDs."""
    start = time.perf_counter()
    correlation_id = request.headers.get("x-correlation-id", str(uuid4()))
    request.state.correlation_id = correlation_id

    try:
        response = await call_next(request)
    except Exception as exc:
        duration = (time.perf_counter() - start) * 1000
        error_entry = {
            "timestamp": dt.utcnow().isoformat(),
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
        "timestamp": dt.utcnow().isoformat(),
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

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "auth"}

@app.on_event("startup")
async def create_demo_user():
    from .database import SessionLocal
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == "demo").first()
        if not existing_user:
            demo_user = User(
                username="demo",
                email="demo@healthcare.com",
                hashed_password=get_password_hash("demo123"),
                role="patient",
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            print("✅ Demo user created: demo/demo123")
        else:
            print(f"✅ Demo user exists with ID: {existing_user.id}")
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        db.rollback()
    finally:
        db.close()

@app.post("/api/v1/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/v1/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    access_token = create_access_token(
        data={
            "sub": user.id,
            "username": user.username,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
        "user_id": user.id
    }

@app.get("/api/v1/auth/me")
def get_current_user_info(db: Session = Depends(get_db)):
    return {"status": "ok", "message": "Auth service is running"}
