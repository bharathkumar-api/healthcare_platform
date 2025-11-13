#!/bin/bash

echo "========================================="
echo "🔧 Fixing Healthcare Platform"
echo "========================================="

# Fix auth-service schemas.py
cat > auth-service/src/schemas.py << 'SCHEMA'
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "patient"

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        orm_mode = True

class User(UserResponse):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
SCHEMA

# Fix auth-service models.py
cat > auth-service/src/models.py << 'MODEL'
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="patient", nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
MODEL

echo "✅ Fixed auth service files"

# Rebuild services
cd infra
echo "🔨 Rebuilding services..."
docker-compose down
docker-compose up -d --build

echo "⏳ Waiting 15 seconds for services to start..."
sleep 15

# Check services
echo ""
echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "🔍 Checking logs..."
echo "--- Auth Service ---"
docker-compose logs auth-service --tail 10
echo ""
echo "--- Gateway Service ---"
docker-compose logs gateway-service --tail 10

echo ""
echo "🧪 Testing authentication..."
TOKEN=$(curl -s -X POST http://localhost:8090/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo123" 2>&1)

if echo "$TOKEN" | grep -q "access_token"; then
  ACCESS_TOKEN=$(echo "$TOKEN" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
  echo "✅ Login successful!"
  echo "Token: ${ACCESS_TOKEN:0:50}..."
  
  echo ""
  echo "🧪 Testing patient service..."
  PATIENT_RESPONSE=$(curl -s -X GET http://localhost:8090/api/v1/patients/me \
    -H "Authorization: Bearer $ACCESS_TOKEN" 2>&1)
  
  if echo "$PATIENT_RESPONSE" | grep -q "detail\|id"; then
    echo "✅ Patient service responding"
  else
    echo "❌ Patient service error:"
    echo "$PATIENT_RESPONSE"
  fi
  
  echo ""
  echo "🧪 Testing appointment service..."
  APPT_RESPONSE=$(curl -s -X GET http://localhost:8090/api/v1/appointments/ \
    -H "Authorization: Bearer $ACCESS_TOKEN" 2>&1)
  
  if echo "$APPT_RESPONSE" | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ Appointment service responding"
  else
    echo "❌ Appointment service error:"
    echo "$APPT_RESPONSE" | head -5
  fi
  
  echo ""
  echo "🧪 Testing notification service..."
  NOTIF_RESPONSE=$(curl -s -X GET http://localhost:8090/api/v1/notifications/connections \
    -H "Authorization: Bearer $ACCESS_TOKEN" 2>&1)
  
  if echo "$NOTIF_RESPONSE" | python3 -m json.tool > /dev/null 2>&1; then
    echo "✅ Notification service responding"
  else
    echo "❌ Notification service error:"
    echo "$NOTIF_RESPONSE" | head -5
  fi
  
else
  echo "❌ Login failed!"
  echo "Response: $TOKEN"
  echo ""
  echo "Checking auth service logs..."
  docker-compose logs auth-service --tail 30
fi

echo ""
echo "========================================="
echo "🎯 Quick Access"
echo "========================================="
echo "UI:       http://localhost:3000"
echo "Gateway:  http://localhost:8090"
echo "MailHog:  http://localhost:8025"
echo ""
echo "Login:    demo / demo123"
echo "========================================="
