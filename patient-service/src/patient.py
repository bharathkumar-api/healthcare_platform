from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Patient(BaseModel):
    id: int
    name: str
    age: int
    medical_history: str

# In-memory storage for demonstration purposes
patients_db = []

@router.post("/patients/", response_model=Patient)
def create_patient(patient: Patient):
    patients_db.append(patient)
    return patient

@router.get("/patients/", response_model=List[Patient])
def get_patients():
    return patients_db

@router.get("/patients/{patient_id}", response_model=Patient)
def get_patient(patient_id: int):
    for patient in patients_db:
        if patient.id == patient_id:
            return patient
    raise HTTPException(status_code=404, detail="Patient not found")

@router.put("/patients/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, updated_patient: Patient):
    for index, patient in enumerate(patients_db):
        if patient.id == patient_id:
            patients_db[index] = updated_patient
            return updated_patient
    raise HTTPException(status_code=404, detail="Patient not found")

@router.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    for index, patient in enumerate(patients_db):
        if patient.id == patient_id:
            del patients_db[index]
            return {"detail": "Patient deleted"}
    raise HTTPException(status_code=404, detail="Patient not found")