#!/bin/bash
# Complete test of the student API

echo "🧪 Testing Student API - Complete Flow"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if API is running
echo "1️⃣  Checking if API is running..."
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
if [[ $HEALTH == *"healthy"* ]]; then
    echo -e "${GREEN}✅ API is running${NC}"
else
    echo -e "${RED}❌ API is not running${NC}"
    echo "Start it with: ./start_student_api.sh"
    exit 1
fi

echo ""
echo "2️⃣  Sending test task request..."

# Send a test request
RESPONSE=$(curl -s -X POST http://localhost:8000/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24f1002102@ds.study.iitm.ac.in",
    "secret": "AlanJoanna123#",
    "task": "test-hello-'$(date +%s)'",
    "round": 1,
    "nonce": "test-'$(date +%s)'",
    "brief": "Create a simple HTML page with an h1 tag with id=\"greeting\" that displays \"Hello World\". Use Bootstrap 5 from CDN for styling.",
    "checks": [
      "Repo has MIT license",
      "README.md is professional",
      "Page has h1#greeting element",
      "h1#greeting displays Hello World"
    ],
    "evaluation_url": "http://localhost:8001/api/evaluate",
    "attachments": []
  }')

echo "Response: $RESPONSE"
echo ""

if [[ $RESPONSE == *"processing"* ]] || [[ $RESPONSE == *"received"* ]]; then
    echo -e "${GREEN}✅ Task request accepted${NC}"
    echo ""
    echo -e "${YELLOW}📊 Monitor the logs in the terminal where the API is running${NC}"
    echo -e "${YELLOW}🔍 Check GitHub for new repo after ~60 seconds${NC}"
    echo ""
    echo "Expected repo name: test-hello-XXXXXXXXXX-r1"
    echo "GitHub URL: https://github.com/24f1002102?tab=repositories"
else
    echo -e "${RED}❌ Task request failed${NC}"
    exit 1
fi

echo ""
echo "✅ Test complete!"
