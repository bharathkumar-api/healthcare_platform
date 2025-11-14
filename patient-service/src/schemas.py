from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date

class PatientBase(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_number: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MedicalRecordBase(BaseModel):
    record_type: str
    title: str
    description: Optional[str] = None
    doctor_name: Optional[str] = None

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordResponse(MedicalRecordBase):
    id: int
    patient_id: int
    record_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class AllergyBase(BaseModel):
    allergen: str
    severity: str
    reaction: Optional[str] = None
    diagnosed_date: Optional[date] = None

class AllergyCreate(AllergyBase):
    pass

class AllergyResponse(AllergyBase):
    id: int
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MedicationBase(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    prescribed_by: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True
    notes: Optional[str] = None

class MedicationCreate(MedicationBase):
    pass

class MedicationResponse(MedicationBase):
    id: int
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True
