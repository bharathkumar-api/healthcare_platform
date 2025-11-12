from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True)
    provider_id = Column(Integer, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default='pending')
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, index=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime)
    payment_method = Column(String)  # e.g., 'credit_card', 'insurance'
    status = Column(String, default='completed')