#!/bin/bash

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🏥 Healthcare Platform - Interactive Demo                 ║"
echo "║     Microservices Architecture with Real-time Notifications   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get token
echo -e "${BLUE}🔐 Authenticating...${NC}"
TOKEN=$(curl -s -X POST http://localhost:8090/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo -e "${RED}❌ Failed to authenticate${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Authenticated successfully!${NC}"
echo ""

# Function to pause
pause() {
    echo ""
    read -p "Press Enter to continue..."
    echo ""
}

# Demo scenarios
echo "════════════════════════════════════════════════════════════════"
echo "                    DEMO SCENARIO START"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Scenario 1: New patient onboarding
echo -e "${BLUE}📋 SCENARIO 1: New Patient Onboarding${NC}"
echo "Patient 'John Demo' is registering in the healthcare system..."
pause

echo "Creating patient profile..."
curl -s -X POST http://localhost:8090/api/v1/patients/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date_of_birth": "1990-05-15",
    "gender": "Male",
    "blood_type": "A+",
    "phone": "+1-555-1234",
    "address": "123 Healthcare Ave, Medical City, HC 12345",
    "emergency_contact": "Jane Doe",
    "emergency_phone": "+1-555-5678",
    "insurance_provider": "HealthFirst Insurance",
    "insurance_number": "HF-123456789"
  }' | python3 -m json.tool

echo -e "${GREEN}✅ Patient profile created${NC}"
pause

# Scenario 2: Adding medical history
echo -e "${BLUE}�� SCENARIO 2: Adding Medical History${NC}"
echo "Adding patient's allergies and medications..."
pause

echo "Adding allergy to Penicillin..."
curl -s -X POST http://localhost:8090/api/v1/patients/allergies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "allergen": "Penicillin",
    "severity": "Severe",
    "reaction": "Anaphylaxis, breathing difficulty",
    "diagnosed_date": "2015-03-20"
  }' | python3 -m json.tool

echo ""
echo "Adding current medication..."
curl -s -X POST http://localhost:8090/api/v1/patients/medications \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "medication_name": "Lisinopril",
    "dosage": "10mg",
    "frequency": "Once daily",
    "prescribed_by": "Dr. Michael Chen",
    "start_date": "2024-01-15",
    "is_active": true,
    "notes": "Take with breakfast for blood pressure management"
  }' | python3 -m json.tool

echo -e "${GREEN}✅ Medical history updated${NC}"
pause

# Scenario 3: Searching for a specialist
echo -e "${BLUE}🔍 SCENARIO 3: Finding a Cardiologist${NC}"
echo "Patient needs a cardiologist for annual checkup..."
pause

echo "Searching for available cardiologists..."
curl -s -X GET "http://localhost:8090/api/v1/providers/?specialty=Cardiology&available_only=true" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo -e "${YELLOW}ℹ️  Note: Provider list may be empty. Let's create a sample provider.${NC}"
pause

# Scenario 4: Booking an appointment
echo -e "${BLUE}📅 SCENARIO 4: Booking an Appointment${NC}"
echo "Booking appointment with Dr. Emily Rodriguez..."
pause

APPOINTMENT=$(curl -s -X POST http://localhost:8090/api/v1/appointments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_name": "Dr. Emily Rodriguez",
    "specialty": "Cardiology",
    "appointment_date": "2025-11-25T14:30:00",
    "reason": "Annual heart checkup and stress test",
    "status": "scheduled"
  }')

echo "$APPOINTMENT" | python3 -m json.tool

APPOINTMENT_ID=$(echo "$APPOINTMENT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 'N/A'))" 2>/dev/null)

echo -e "${GREEN}✅ Appointment booked successfully! ID: $APPOINTMENT_ID${NC}"
pause

# Scenario 5: Real-time notification
echo -e "${BLUE}🔔 SCENARIO 5: Real-time Appointment Reminder${NC}"
echo "System sends a real-time notification to the patient..."
pause

echo "Sending notification..."
curl -s -X POST http://localhost:8090/api/v1/notifications/push \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "type": "appointment_reminder",
    "title": "Appointment Reminder",
    "message": "Your appointment with Dr. Emily Rodriguez is tomorrow at 2:30 PM",
    "data": {
      "appointment_id": "'$APPOINTMENT_ID'",
      "doctor": "Dr. Emily Rodriguez",
      "time": "2025-11-25T14:30:00",
      "specialty": "Cardiology"
    }
  }' | python3 -m json.tool

echo -e "${GREEN}✅ Notification sent!${NC}"
echo -e "${YELLOW}💡 If WebSocket is connected, the patient receives this instantly!${NC}"
pause

# Scenario 6: Adding lab results
echo -e "${BLUE}🧪 SCENARIO 6: Lab Results Added${NC}"
echo "Doctor adds lab test results to patient's record..."
pause

curl -s -X POST http://localhost:8090/api/v1/patients/medical-records \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "record_type": "Lab Report",
    "title": "Pre-appointment Blood Work",
    "description": "Complete Metabolic Panel: All values within normal range. Cholesterol: 185 mg/dL (Optimal). Blood Sugar: 92 mg/dL (Normal).",
    "doctor_name": "Dr. Sarah Johnson"
  }' | python3 -m json.tool

echo -e "${GREEN}✅ Lab results recorded${NC}"
pause

# View complete patient profile
echo -e "${BLUE}👤 SCENARIO 7: Viewing Complete Patient Profile${NC}"
echo "Retrieving all patient information..."
pause

curl -s -X GET http://localhost:8090/api/v1/patients/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

pause

# Check WebSocket connections
echo -e "${BLUE}🔌 SCENARIO 8: Checking Real-time Connections${NC}"
echo "Viewing active WebSocket connections..."
pause

curl -s -X GET http://localhost:8090/api/v1/notifications/connections \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

pause

# Final summary
clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    DEMO COMPLETE! 🎉                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✅ Successfully Demonstrated:${NC}"
echo "   1. Patient registration and profile management"
echo "   2. Medical history tracking (allergies, medications)"
echo "   3. Provider search functionality"
echo "   4. Appointment booking system"
echo "   5. Real-time push notifications"
echo "   6. Medical records management"
echo "   7. Complete patient data retrieval"
echo "   8. WebSocket connection monitoring"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}📚 Next Steps:${NC}"
echo ""
echo "1. Test WebSocket in browser:"
echo "   open /tmp/test_websocket.html"
echo "   Token: $TOKEN"
echo ""
echo "2. View emails in MailHog:"
echo "   http://localhost:8025"
echo ""
echo "3. Access UI:"
echo "   http://localhost:3000"
echo ""
echo "4. View API Documentation:"
echo "   http://localhost:8090/docs"
echo ""
echo "5. Check service health:"
echo "   curl http://localhost:8090/api/health | jq"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}📊 Your Access Token:${NC}"
echo "   $TOKEN"
echo ""
echo "Save this token to test WebSocket connections!"
echo ""
