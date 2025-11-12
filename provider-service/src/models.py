from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Provider(Base):
    __tablename__ = 'providers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialty = Column(String, index=True)
    contact_info = Column(String)

    appointments = relationship("Appointment", back_populates="provider")

class Specialty(Base):
    __tablename__ = 'specialties'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    providers = relationship("Provider", back_populates="specialty")