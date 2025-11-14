# filepath: /Users/bharathkumarveeramalli/healthcare_platform-2/provider-service/src/models/provider.py
from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from src.database.session import Base

class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(100), nullable=False, index=True)
    qualification = Column(String(255))
    experience_years = Column(Integer)
    rating = Column(Float, default=0.0)
    available = Column(Boolean, default=True, index=True)
    consultation_fee = Column(Float)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255))
