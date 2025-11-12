from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("", response_model=schemas.AppointmentRead, status_code=201)
def create_appt(payload: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    # Simple overlap check (same provider, time window overlap)
    overlapping = db.query(models.Appointment).filter(
        models.Appointment.provider_id == payload.provider_id,
        models.Appointment.starts_at < payload.ends_at,
        models.Appointment.ends_at > payload.starts_at,
        models.Appointment.status == models.ApptStatus.scheduled
    ).first()
    if overlapping:
        raise HTTPException(400, "Provider already has an appointment in this slot")
    obj = models.Appointment(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("", response_model=list[schemas.AppointmentRead])
def list_appts(db: Session = Depends(get_db)):
    return db.query(models.Appointment).order_by(models.Appointment.id.desc()).all()

@router.get("/{appt_id}", response_model=schemas.AppointmentRead)
def get_appt(appt_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Appointment, appt_id)
    if not obj: raise HTTPException(404, "Appointment not found")
    return obj

@router.put("/{appt_id}", response_model=schemas.AppointmentRead)
def update_appt(appt_id: int, payload: schemas.AppointmentUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Appointment, appt_id)
    if not obj: raise HTTPException(404, "Appointment not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/{appt_id}", status_code=204)
def delete_appt(appt_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Appointment, appt_id)
    if not obj: raise HTTPException(404, "Appointment not found")
    db.delete(obj); db.commit(); return