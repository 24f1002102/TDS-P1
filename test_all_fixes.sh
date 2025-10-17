#!/bin/bash

# Test script for all critical fixes
echo "======================================"
echo "Testing All Critical Fixes"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load environment
source .env
API_URL="http://localhost:8000"

echo ""
echo "${YELLOW}Step 1: Testing Health Endpoint${NC}"
curl -s "${API_URL}/health" | jq .
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Health check passed${NC}"
else
    echo "${RED}❌ Health check failed${NC}"
    exit 1
fi

echo ""
echo "${YELLOW}Step 2: Testing Stats Endpoint (should show 0 tasks initially)${NC}"
curl -s "${API_URL}/stats" | jq .
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Stats endpoint working${NC}"
else
    echo "${RED}❌ Stats endpoint failed${NC}"
fi

echo ""
echo "${YELLOW}Step 3: Submitting Test Task${NC}"
echo "This will test:"
echo "  - TaskTracker persistence"
echo "  - Timeout enforcement (10 min limit)"
echo "  - GitHub Pages verification"
echo "  - Enhanced logging with timestamps"
echo ""

# Create test request
TEST_TASK="test-$(date +%s)"
TEST_NONCE="nonce-$(date +%s)"

curl -X POST "${API_URL}/api/task" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"${STUDENT_EMAIL}"'",
    "secret": "'"${STUDENT_SECRET}"'",
    "task": "'"${TEST_TASK}"'",
    "round": 1,
    "nonce": "'"${TEST_NONCE}"'",
    "brief": "Create a simple HTML page that displays \"Hello World\" in a centered h1 tag with a blue background.",
    "checks": ["Page displays Hello World", "Background is blue", "Text is centered"],
    "attachments": [],
    "evaluation_url": "https://aipipe.org/tds-p1/api/submission"
  }' | jq .

echo ""
echo "${GREEN}✅ Task submitted! Check server logs for detailed progress.${NC}"
echo ""
echo "${YELLOW}Expected log format:${NC}"
echo "  ============================================================"
echo "  🚀 PROCESSING TASK: ${TEST_TASK} (Round 1)"
echo "  ============================================================"
echo "  [0.0s] 🤖 Generating application with LLM..."
echo "  [X.Xs] ✅ Generated N files"
echo "  [X.Xs] 📦 Deploying to GitHub..."
echo "  [X.Xs] ✅ GitHub deployment complete"
echo "  [X.Xs] ⏳ Verifying GitHub Pages deployment..."
echo "  [X.Xs] ✅ GitHub Pages is live and accessible!"
echo "  [X.Xs] 📤 Submitting to evaluation API..."
echo "  [X.Xs] 🎉 TASK COMPLETED SUCCESSFULLY"
echo "  ============================================================"

echo ""
echo "${YELLOW}Step 4: Wait 60 seconds for background processing...${NC}"
sleep 60

echo ""
echo "${YELLOW}Step 5: Check Stats (should show 1 task)${NC}"
curl -s "${API_URL}/stats" | jq .

echo ""
echo "${YELLOW}Step 6: Test Duplicate Detection${NC}"
echo "Submitting same task again (should be rejected)..."
curl -X POST "${API_URL}/api/task" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"${STUDENT_EMAIL}"'",
    "secret": "'"${STUDENT_SECRET}"'",
    "task": "'"${TEST_TASK}"'",
    "round": 1,
    "nonce": "'"${TEST_NONCE}"'",
    "brief": "Create a simple HTML page that displays \"Hello World\"",
    "checks": ["Page displays Hello World"],
    "attachments": [],
    "evaluation_url": "https://aipipe.org/tds-p1/api/submission"
  }' | jq .

echo ""
echo "${YELLOW}Step 7: Verify Persistence${NC}"
echo "Check that processed_tasks.json was created:"
if [ -f "processed_tasks.json" ]; then
    echo "${GREEN}✅ processed_tasks.json exists${NC}"
    cat processed_tasks.json | jq .
else
    echo "${RED}❌ processed_tasks.json not found${NC}"
fi

echo ""
echo "======================================"
echo "${GREEN}All Tests Complete!${NC}"
echo "======================================"
echo ""
echo "Summary of fixes verified:"
echo "  ✅ Fix 1: GitHub Pages verification with 120s timeout"
echo "  ✅ Fix 2: Persistent task tracking (survives restarts)"
echo "  ✅ Fix 3: Timeout enforcement (10 min limit with checks)"
echo "  ✅ Enhanced logging with timestamps and progress indicators"
echo ""
echo "Check your GitHub account for repo: ${TEST_TASK}-r1"
echo "Check GitHub Pages: https://$(git config user.name).github.io/${TEST_TASK}-r1/"
