from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    doctor_name = Column(String(255), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    reason = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="scheduled")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
