from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .models import ApptStatus

class AppointmentBase(BaseModel):
    patient_id: int
    provider_id: int
    starts_at: datetime
    ends_at: datetime
    reason: Optional[str] = None
    status: ApptStatus = ApptStatus.scheduled

class AppointmentCreate(AppointmentBase): ...
class AppointmentUpdate(BaseModel):
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    status: Optional[ApptStatus] = None
    reason: Optional[str] = None

class AppointmentRead(AppointmentBase):
    id: int
    class Config: from_attributes = True