from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProviderBase(BaseModel):
    first_name: str
    last_name: str
    specialty: str
    license_number: str
    years_of_experience: int
    consultation_fee: float
    bio: Optional[str] = None
    is_available: bool = True

class ProviderCreate(ProviderBase):
    pass

class ProviderResponse(ProviderBase):
    id: int
    rating: float
    total_reviews: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    rating: float
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    provider_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProviderSearchResponse(BaseModel):
    providers: List[ProviderResponse]
    total: int
    filters: dict
