from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("", response_model=schemas.PatientRead, status_code=201)
def create_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    exists = db.query(models.Patient).filter(models.Patient.email == payload.email).first()
    if exists: raise HTTPException(400, "Email already exists")
    obj = models.Patient(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("/{patient_id}", response_model=schemas.PatientRead)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Patient, patient_id)
    if not obj: raise HTTPException(404, "Patient not found")
    return obj

@router.get("", response_model=list[schemas.PatientRead])
def list_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).order_by(models.Patient.id.desc()).all()

@router.put("/{patient_id}", response_model=schemas.PatientRead)
def update_patient(patient_id: int, payload: schemas.PatientUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Patient, patient_id)
    if not obj: raise HTTPException(404, "Patient not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Patient, patient_id)
    if not obj: raise HTTPException(404, "Patient not found")
    db.delete(obj); db.commit(); return