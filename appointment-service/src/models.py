from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Appointment(BaseModel):
    id: int
    patient_id: int
    provider_id: int
    appointment_time: datetime
    reason: Optional[str] = None
    status: str  # e.g., 'scheduled', 'completed', 'canceled'

class AppointmentCreate(BaseModel):
    patient_id: int
    provider_id: int
    appointment_time: datetime
    reason: Optional[str] = None

class AppointmentUpdate(BaseModel):
    appointment_time: Optional[datetime] = None
    reason: Optional[str] = None
    status: Optional[str] = None