from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    specialty = Column(String(100), nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    years_of_experience = Column(Integer)
    education = Column(Text)
    certifications = Column(Text)
    bio = Column(Text)
    consultation_fee = Column(Float)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    schedules = relationship("ProviderSchedule", back_populates="provider", cascade="all, delete-orphan")
    reviews = relationship("ProviderReview", back_populates="provider", cascade="all, delete-orphan")

class ProviderSchedule(Base):
    __tablename__ = "provider_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    provider = relationship("Provider", back_populates="schedules")

class ProviderReview(Base):
    __tablename__ = "provider_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    patient_id = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    provider = relationship("Provider", back_populates="reviews")
