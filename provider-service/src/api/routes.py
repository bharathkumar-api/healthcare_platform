from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database.session import get_db
from src.models.provider import Provider
from pydantic import BaseModel

router = APIRouter()

class ProviderResponse(BaseModel):
    id: int
    name: str
    specialty: str
    qualification: str
    experience_years: int
    rating: float
    available: bool
    consultation_fee: float
    address: str
    phone: str
    email: str

    class Config:
        from_attributes = True

@router.get("/providers/", response_model=List[ProviderResponse])
def search_providers(
    specialty: Optional[str] = Query(None),
    available_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Search for healthcare providers"""
    query = db.query(Provider)
    
    if specialty:
        query = query.filter(Provider.specialty == specialty)
    
    if available_only:
        query = query.filter(Provider.available == True)
    
    providers = query.order_by(Provider.rating.desc()).all()
    return providers

@router.get("/providers/{provider_id}", response_model=ProviderResponse)
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    """Get a specific provider"""
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider
