#!/bin/bash

echo "🔌 WebSocket Connection Test"
echo "=============================="
echo ""

# Get token
echo "Getting authentication token..."
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
echo "WebSocket URL:"
echo "ws://localhost:8090/ws/notifications/1?token=$TOKEN"
echo ""
echo "Opening test page..."
open /tmp/test_websocket.html 2>/dev/null

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Instructions:"
echo "═══════════════════════════════════════════════════════════"
echo "1. The test page should open in your browser"
echo "2. Paste this token in the Token field:"
echo ""
echo "   $TOKEN"
echo ""
echo "3. Click 'Connect'"
echo "4. You should see 'Status: Connected' in green"
echo "5. Click 'Send Test Notification' to test"
echo ""
echo "To send notifications from terminal:"
echo ""
echo "curl -X POST http://localhost:8090/api/v1/notifications/push \\"
echo "  -H \"Authorization: Bearer $TOKEN\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{"
echo "    \"user_id\": 1,"
echo "    \"type\": \"test\","
echo "    \"title\": \"Test from Terminal\","
echo "    \"message\": \"This is a test notification\""
echo "  }'"
echo ""
