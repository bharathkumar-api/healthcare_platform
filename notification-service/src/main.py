from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from .email import send_appointment_confirmation, send_email

app = FastAPI(title="Notification Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailNotification(BaseModel):
    to_email: EmailStr
    subject: str
    body: str

class AppointmentNotification(BaseModel):
    to_email: EmailStr
    appointment_details: dict

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "notification"}

@app.post("/api/v1/notifications/send-email")
def send_notification_email(notification: EmailNotification):
    success = send_email(notification.to_email, notification.subject, notification.body)
    if success:
        return {"message": "Email sent successfully"}
    raise HTTPException(status_code=500, detail="Failed to send email")

@app.post("/api/v1/notifications/appointment")
def send_appointment_notification(notification: AppointmentNotification):
    success = send_appointment_confirmation(notification.to_email, notification.appointment_details)
    if success:
        return {"message": "Notification sent successfully"}
    raise HTTPException(status_code=500, detail="Failed to send notification")
