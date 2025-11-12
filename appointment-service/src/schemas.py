from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentCreate(BaseModel):
    doctor_name: str
    appointment_date: datetime
    reason: str
    notes: Optional[str] = None
    status: Optional[str] = "scheduled"

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_name: str
    appointment_date: datetime
    reason: str
    notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True