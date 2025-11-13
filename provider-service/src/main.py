from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import json

from .database import engine, get_db, Base
from .models import Provider, ProviderSchedule, ProviderReview
from .schemas import (
    ProviderCreate, ProviderResponse, ProviderUpdate, ProviderDetailResponse,
    ProviderScheduleCreate, ProviderScheduleResponse,
    ProviderReviewCreate, ProviderReviewResponse,
    ProviderSearchResponse
)

Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Provider Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def log_action(correlation_id: str, action: str, user_id: Optional[int], details: dict):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "correlation_id": correlation_id,
        "service": "provider-service",
        "action": action,
        "user_id": user_id,
        "details": details
    }
    logger.info(json.dumps(log_entry))

def get_current_user(
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    x_correlation_id: Optional[str] = Header(None)
):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "user_id": int(x_user_id),
        "role": x_user_role or "patient",
        "correlation_id": x_correlation_id or "unknown"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "provider-service"}

@app.post("/api/v1/providers/", response_model=ProviderResponse, status_code=201)
def create_provider_profile(
    provider: ProviderCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]
    role = current_user["role"]
    
    if role not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Only doctors can create provider profiles")
    
    existing = db.query(Provider).filter(Provider.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Provider profile already exists")
    
    db_provider = Provider(user_id=user_id, **provider.dict())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    
    log_action(current_user["correlation_id"], "create_provider_profile", user_id, {"provider_id": db_provider.id})
    return db_provider

@app.get("/api/v1/providers/", response_model=ProviderSearchResponse)
def search_providers(
    specialty: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None),
    available_only: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Provider)
    
    if specialty:
        query = query.filter(Provider.specialty.ilike(f"%{specialty}%"))
    
    if min_rating:
        query = query.filter(Provider.rating >= min_rating)
    
    if available_only:
        query = query.filter(Provider.is_available == True)
    
    total = query.count()
    providers = query.order_by(Provider.rating.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    log_action(current_user["correlation_id"], "search_providers", current_user["user_id"], {
        "specialty": specialty, "total_found": total
    })
    
    return {"providers": providers, "total": total, "page": page, "page_size": page_size}

@app.get("/api/v1/providers/{provider_id}", response_model=ProviderDetailResponse)
def get_provider(
    provider_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider
