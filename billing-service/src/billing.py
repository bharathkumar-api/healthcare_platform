from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class Invoice(BaseModel):
    id: int
    patient_id: int
    amount: float
    status: str

class Payment(BaseModel):
    id: int
    invoice_id: int
    amount: float
    payment_date: str

invoices = []
payments = []

@router.post("/invoices/", response_model=Invoice)
def create_invoice(invoice: Invoice):
    invoices.append(invoice)
    return invoice

@router.get("/invoices/", response_model=List[Invoice])
def get_invoices():
    return invoices

@router.post("/payments/", response_model=Payment)
def create_payment(payment: Payment):
    if payment.invoice_id not in [invoice.id for invoice in invoices]:
        raise HTTPException(status_code=404, detail="Invoice not found")
    payments.append(payment)
    return payment

@router.get("/payments/", response_model=List[Payment])
def get_payments():
    return payments

@router.get("/invoices/{invoice_id}", response_model=Invoice)
def get_invoice(invoice_id: int):
    for invoice in invoices:
        if invoice.id == invoice_id:
            return invoice
    raise HTTPException(status_code=404, detail="Invoice not found")