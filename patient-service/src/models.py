from pydantic import BaseModel
from typing import Optional
from datetime import date

class Patient(BaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    medical_history: Optional[str] = None

class MedicalRecord(BaseModel):
    patient_id: int
    record_date: date
    description: str
    doctor_id: int
    notes: Optional[str] = None