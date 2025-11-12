from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class Appointment(BaseModel):
    id: int
    patient_id: int
    provider_id: int
    appointment_time: datetime
    reason: str

appointments = []

@router.post("/appointments/", response_model=Appointment)
def create_appointment(appointment: Appointment):
    appointments.append(appointment)
    return appointment

@router.get("/appointments/", response_model=List[Appointment])
def get_appointments():
    return appointments

@router.get("/appointments/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: int):
    for appointment in appointments:
        if appointment.id == appointment_id:
            return appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int):
    global appointments
    appointments = [appointment for appointment in appointments if appointment.id != appointment_id]
    return {"detail": "Appointment deleted"}