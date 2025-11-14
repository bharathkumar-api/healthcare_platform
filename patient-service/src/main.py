from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging
import json
import time
from uuid import uuid4
from datetime import datetime

from .database import engine, Base, get_db
from .models import Patient, MedicalRecord, Allergy, Medication
from .schemas import (
    PatientCreate, PatientResponse, PatientUpdate,
    MedicalRecordCreate, MedicalRecordResponse,
    AllergyCreate, AllergyResponse,
    MedicationCreate, MedicationResponse
)
from .core.auth import get_current_user

SERVICE_NAME = "patient-service"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(SERVICE_NAME)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patient Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Structured logging with correlation IDs for every request."""
    start = time.perf_counter()
    correlation_id = request.headers.get("x-correlation-id", str(uuid4()))
    request.state.correlation_id = correlation_id
    response = None
    try:
        response = await call_next(request)
    except Exception as exc:
        duration = (time.perf_counter() - start) * 1000
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": SERVICE_NAME,
            "method": request.method,
            "path": request.url.path,
            "status": 500,
            "duration_ms": round(duration, 2),
            "correlation_id": correlation_id,
            "user_id": getattr(request.state, "user_id", None),
            "error": str(exc)
        }
        logger.exception(json.dumps(error_entry))
        raise

    duration = (time.perf_counter() - start) * 1000
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": SERVICE_NAME,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round(duration, 2),
        "correlation_id": correlation_id,
        "user_id": getattr(request.state, "user_id", None)
    }

    if response.status_code >= 500:
        logger.error(json.dumps(log_entry))
    elif response.status_code >= 400:
        logger.warning(json.dumps(log_entry))
    else:
        logger.info(json.dumps(log_entry))

    response.headers["X-Correlation-ID"] = correlation_id
    return response

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "patient"}

@app.post("/api/v1/patients/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_patient(patient_data: PatientCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    existing_patient = db.query(Patient).filter(Patient.user_id == current_user["user_id"]).first()
    
    if existing_patient:
        for key, value in patient_data.dict(exclude_unset=True).items():
            setattr(existing_patient, key, value)
        db.commit()
        db.refresh(existing_patient)
        return existing_patient
    
    new_patient = Patient(**patient_data.dict(), user_id=current_user["user_id"])
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@app.get("/api/v1/patients/me", response_model=PatientResponse)
def get_my_profile(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.user_id == current_user["user_id"]).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return patient

@app.put("/api/v1/patients/me", response_model=PatientResponse)
def update_my_profile(patient_data: PatientUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.user_id == current_user["user_id"]).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    
    for key, value in patient_data.dict(exclude_unset=True).items():
        setattr(patient, key, value)
    
    db.commit()
    db.refresh(patient)
    return patient

@app.post("/api/v1/patients/medical-records", response_model=MedicalRecordResponse)
def create_medical_record(record: MedicalRecordCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.user_id == current_user["user_id"]).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    
    new_record = MedicalRecord(**record.dict(), patient_id=patient.id)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@app.get("/api/v1/patients/medical-records", response_model=List[MedicalRecordResponse])
def get_medical_records(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.user_id == current_user["user_id"]).first()
    if not patient:
        return []
    return db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient.id).all()

@app.post("/api/v1/patients/allergies", response_model=AllergyResponse)
def create_allergy(allergy: AllergyCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.user_id == current_user["user_id"]).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    
    new_allergy = Allergy(**allergy.dict(), patient_id=patient.id)
    db.add(new_allergy)
    db.commit()
    db.refresh(new_allergy)
    return new_allergy

@app.get("/api/v1/patients/allergies", response_model=List[AllergyResponse])
def get_allergies(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.user_id == current_user["user_id"]).first()
    if not patient:
        return []
    return db.query(Allergy).filter(Allergy.patient_id == patient.id).all()

@app.post("/api/v1/patients/medications", response_model=MedicationResponse)
def create_medication(medication: MedicationCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.user_id == current_user["user_id"]).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    
    new_medication = Medication(**medication.dict(), patient_id=patient.id)
    db.add(new_medication)
    db.commit()
    db.refresh(new_medication)
    return new_medication

@app.get("/api/v1/patients/medications", response_model=List[MedicationResponse])
def get_medications(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.user_id == current_user["user_id"]).first()
    if not patient:
        return []
    return db.query(Medication).filter(Medication.patient_id == patient.id).all()
