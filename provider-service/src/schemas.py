from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProviderBase(BaseModel):
    specialty: str
    license_number: str
    years_of_experience: Optional[int] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    bio: Optional[str] = None
    consultation_fee: Optional[float] = None
    is_available: bool = True

class ProviderCreate(ProviderBase):
    pass

class ProviderUpdate(BaseModel):
    specialty: Optional[str] = None
    years_of_experience: Optional[int] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    bio: Optional[str] = None
    consultation_fee: Optional[float] = None
    is_available: Optional[bool] = None

class ProviderResponse(ProviderBase):
    id: int
    user_id: int
    rating: float
    total_reviews: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProviderScheduleBase(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool = True

class ProviderScheduleCreate(ProviderScheduleBase):
    pass

class ProviderScheduleResponse(ProviderScheduleBase):
    id: int
    provider_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProviderReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None

class ProviderReviewCreate(ProviderReviewBase):
    provider_id: int

class ProviderReviewResponse(ProviderReviewBase):
    id: int
    provider_id: int
    patient_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProviderDetailResponse(ProviderResponse):
    schedules: List[ProviderScheduleResponse] = []
    reviews: List[ProviderReviewResponse] = []

class ProviderSearchResponse(BaseModel):
    providers: List[ProviderResponse]
    total: int
    page: int
    page_size: int
