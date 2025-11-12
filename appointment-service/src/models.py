from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, String
from sqlalchemy.sql import func
from .database import Base
import enum

class ApptStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    canceled = "canceled"

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)   # FK to patient-service (logical)
    provider_id = Column(Integer, nullable=False)  # FK to provider-service (logical)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(ApptStatus), default=ApptStatus.scheduled, nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())