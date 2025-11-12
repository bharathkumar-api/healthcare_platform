from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from .database import engine, Base, get_db
from .models import Appointment
from .schemas import AppointmentCreate, AppointmentResponse
from .auth import get_current_user

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Appointment Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "appointment"}

@app.post("/api/v1/appointments/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_appointment = Appointment(
        patient_id=current_user["user_id"],
        doctor_name=appointment.doctor_name,
        appointment_date=appointment.appointment_date,
        reason=appointment.reason,
        notes=appointment.notes,
        status=appointment.status
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@app.get("/api/v1/appointments/", response_model=List[AppointmentResponse])
def get_appointments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == current_user["user_id"]
    ).order_by(Appointment.appointment_date.desc()).all()
    return appointments

@app.get("/api/v1/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == current_user["user_id"]
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return appointment

@app.put("/api/v1/appointments/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == current_user["user_id"]
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.doctor_name = appointment_update.doctor_name
    appointment.appointment_date = appointment_update.appointment_date
    appointment.reason = appointment_update.reason
    appointment.notes = appointment_update.notes
    appointment.status = appointment_update.status
    
    db.commit()
    db.refresh(appointment)
    return appointment

@app.delete("/api/v1/appointments/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == current_user["user_id"]
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db.delete(appointment)
    db.commit()
    return {"message": "Appointment deleted successfully"}
