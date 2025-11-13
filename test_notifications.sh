#!/bin/bash

echo "🔔 Testing Notification System"
echo "==============================="
echo ""

# Get token
echo "1. Getting authentication token..."
TOKEN=$(curl -s -X POST http://localhost:8090/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    exit 1
fi

echo "✅ Token obtained"
echo ""

# Test 1: Check service health
echo "2. Checking notification service health..."
echo "   Direct (port 8004):"
curl -s http://localhost:8004/health | python3 -m json.tool
echo ""
echo "   Through Gateway (port 8090):"
curl -s http://localhost:8090/api/health | python3 -m json.tool | grep -A 5 notification
echo ""

# Test 2: Check active connections
echo "3. Checking active WebSocket connections..."
curl -s http://localhost:8090/api/v1/notifications/connections \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# Test 3: Send push notification
echo "4. Sending push notification..."
RESPONSE=$(curl -s -X POST http://localhost:8090/api/v1/notifications/push \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "type": "test",
    "title": "Test Notification",
    "message": "This is a test notification sent at '$(date +"%H:%M:%S")'",
    "data": {
      "test": true,
      "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%S")'"
    }
  }')

echo "$RESPONSE" | python3 -m json.tool

if echo "$RESPONSE" | grep -q "sent\|no_connections"; then
    echo "✅ Notification API working"
else
    echo "❌ Notification API failed"
fi
echo ""

# Test 4: Send email notification
echo "5. Sending email notification..."
EMAIL_RESPONSE=$(curl -s -X POST http://localhost:8090/api/v1/notifications/email \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "patient@example.com",
    "subject": "Test Email from Healthcare Platform",
    "body": "This is a test email sent at '$(date +"%H:%M:%S")'"
  }')

echo "$EMAIL_RESPONSE" | python3 -m json.tool

if echo "$EMAIL_RESPONSE" | grep -q "sent"; then
    echo "✅ Email notification working"
    echo "   Check MailHog at http://localhost:8025"
else
    echo "❌ Email notification failed"
fi
echo ""

echo "════════════════════════════════════════"
echo "Summary:"
echo "  - API Gateway: http://localhost:8090"
echo "  - Notification Service: http://localhost:8004"
echo "  - MailHog (Email): http://localhost:8025"
echo "  - WebSocket: ws://localhost:8004/ws/1"
echo ""
echo "To test WebSocket in UI:"
echo "  1. Open http://localhost:3000"
echo "  2. Login with demo/demo123"
echo "  3. Check connection status in header"
echo "  4. Go to Notifications tab"
echo "  5. Click 'Send Test Notification'"
echo "════════════════════════════════════════"
