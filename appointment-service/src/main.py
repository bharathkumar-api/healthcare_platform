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
from .models import Appointment
from .schemas import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from .core.auth import get_current_user

SERVICE_NAME = "appointment-service"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(SERVICE_NAME)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Appointment Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Structured logging middleware with correlation IDs."""
    start = time.perf_counter()
    correlation_id = request.headers.get("x-correlation-id", str(uuid4()))
    request.state.correlation_id = correlation_id

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
    return {"status": "healthy", "service": "appointment"}

@app.post("/api/v1/appointments/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    new_appointment = Appointment(**appointment.dict(), user_id=current_user["user_id"])
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

@app.get("/api/v1/appointments/", response_model=List[AppointmentResponse])
def get_appointments(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    appointments = db.query(Appointment).filter(Appointment.user_id == current_user["user_id"]).order_by(Appointment.appointment_date.desc()).all()
    return appointments

@app.get("/api/v1/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.user_id == current_user["user_id"]
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    
    return appointment

@app.put("/api/v1/appointments/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: int, appointment_update: AppointmentUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.user_id == current_user["user_id"]
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    
    for key, value in appointment_update.dict(exclude_unset=True).items():
        setattr(appointment, key, value)
    
    db.commit()
    db.refresh(appointment)
    return appointment

@app.delete("/api/v1/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.user_id == current_user["user_id"]
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    
    db.delete(appointment)
    db.commit()
    return None
