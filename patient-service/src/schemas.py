from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    dob: Optional[date] = None
    active: bool = True

class PatientCreate(PatientBase): ...
class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    active: Optional[bool] = None

class PatientRead(PatientBase):
    id: int
    class Config: from_attributes = True