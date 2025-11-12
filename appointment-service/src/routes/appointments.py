from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Appointment
from ..schemas import AppointmentCreate, AppointmentResponse
from jose import JWTError, jwt
import os

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production-12345")
ALGORITHM = "HS256"

print(f"[APPOINTMENTS] Using SECRET_KEY: {SECRET_KEY}")
print(f"[APPOINTMENTS] Using ALGORITHM: {ALGORITHM}")

def get_current_user(authorization: str = Header(None)):
    print(f"[APPOINTMENTS] Authorization header: {authorization[:50] if authorization else 'None'}...")
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        token = authorization.replace("Bearer ", "").strip()
        print(f"[APPOINTMENTS] Token (first 50 chars): {token[:50]}...")
        print(f"[APPOINTMENTS] Using SECRET_KEY for decode: {SECRET_KEY}")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"[APPOINTMENTS] Token decoded successfully: {payload}")
        
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        return {"username": username, "user_id": user_id, "role": role}
    except JWTError as e:
        print(f"[APPOINTMENTS] JWT Error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=401, detail=f"JWT Error: {str(e)}")
    except Exception as e:
        print(f"[APPOINTMENTS] General error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Auth error: {str(e)}")

@router.post("/", response_model=AppointmentResponse)
def create_appointment(
    appointment: AppointmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]
    
    db_appointment = Appointment(
        patient_id=user_id,
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

@router.get("/", response_model=List[AppointmentResponse])
def get_appointments(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == user_id
    ).order_by(Appointment.appointment_date.desc()).all()
    return appointments

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == user_id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return appointment

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]
    db_appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == user_id
    ).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db_appointment.doctor_name = appointment_update.doctor_name
    db_appointment.appointment_date = appointment_update.appointment_date
    db_appointment.reason = appointment_update.reason
    db_appointment.notes = appointment_update.notes
    db_appointment.status = appointment_update.status
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]
    db_appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == user_id
    ).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db.delete(db_appointment)
    db.commit()
    return {"message": "Appointment deleted successfully"}
