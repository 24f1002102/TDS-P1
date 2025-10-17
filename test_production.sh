#!/bin/bash

# Production API Test Script for Render Deployment
# URL: https://tds-student-api-latest.onrender.com

API_URL="https://tds-student-api-latest.onrender.com"

# Load credentials from .env
source .env

echo "======================================"
echo "🌐 Testing Production API on Render"
echo "======================================"
echo ""
echo "API URL: $API_URL"
echo ""

# Test 1: Root Endpoint
echo "=== Test 1: Root Endpoint ==="
curl -s "$API_URL/" | jq .
echo ""

# Test 2: Health Check
echo "=== Test 2: Health Check ==="
curl -s "$API_URL/health" | jq .
echo ""

# Test 3: Stats Endpoint
echo "=== Test 3: Stats (before submission) ==="
curl -s "$API_URL/stats" | jq .
echo ""

# Test 4: Task Submission - Simple Test
echo "=== Test 4: Task Submission - Simple HTML Page ==="
TASK_ID="render-test-$(date +%s)"
NONCE="nonce-$(date +%s)"

curl -X POST "$API_URL/api/task" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"$STUDENT_EMAIL"'",
    "secret": "'"$STUDENT_SECRET"'",
    "task": "'"$TASK_ID"'",
    "round": 1,
    "nonce": "'"$NONCE"'",
    "brief": "Create a simple HTML page that displays Hello from Render in a large centered h1 tag with a gradient background from blue to green",
    "checks": [
      "Page displays Hello from Render text",
      "Text is centered",
      "Background has blue to green gradient"
    ],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }' | jq .

echo ""
echo "✅ Task submitted: $TASK_ID"
echo "📍 Expected GitHub Repo: https://github.com/$GITHUB_USERNAME/${TASK_ID}-r1"
echo "🌐 Expected GitHub Pages: https://$GITHUB_USERNAME.github.io/${TASK_ID}-r1/"
echo ""
echo "⏳ Wait 60 seconds for processing..."
sleep 60

# Test 5: Check Stats After Submission
echo ""
echo "=== Test 5: Stats (after submission) ==="
curl -s "$API_URL/stats" | jq .
echo ""

# Test 6: Round 2 Submission (Modification)
echo "=== Test 6: Round 2 - Modify Previous Task ==="
NONCE2="nonce-$(date +%s)"

curl -X POST "$API_URL/api/task" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"$STUDENT_EMAIL"'",
    "secret": "'"$STUDENT_SECRET"'",
    "task": "'"$TASK_ID"'",
    "round": 2,
    "nonce": "'"$NONCE2"'",
    "brief": "Modify the page to display Hello from Render - Round 2 with a purple to pink gradient background and add a bouncing animation to the text",
    "checks": [
      "Page displays Hello from Render - Round 2",
      "Background has purple to pink gradient",
      "Text has bouncing animation"
    ],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }' | jq .

echo ""
echo "✅ Round 2 submitted for task: $TASK_ID"
echo ""
echo "⏳ Wait 60 seconds for processing..."
sleep 60

# Test 7: Final Stats
echo ""
echo "=== Test 7: Final Stats ==="
curl -s "$API_URL/stats" | jq .
echo ""

# Test 8: Duplicate Detection
echo "=== Test 8: Duplicate Detection Test ==="
echo "Submitting the same task again (should be rejected)..."
curl -X POST "$API_URL/api/task" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"$STUDENT_EMAIL"'",
    "secret": "'"$STUDENT_SECRET"'",
    "task": "'"$TASK_ID"'",
    "round": 1,
    "nonce": "'"$NONCE"'",
    "brief": "test",
    "checks": ["test"],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }' | jq .

echo ""
echo ""
echo "======================================"
echo "✅ All Tests Complete!"
echo "======================================"
echo ""
echo "📊 Summary:"
echo "  - API URL: $API_URL"
echo "  - Task ID: $TASK_ID"
echo "  - GitHub Repo: https://github.com/$GITHUB_USERNAME/${TASK_ID}-r1"
echo "  - GitHub Pages: https://$GITHUB_USERNAME.github.io/${TASK_ID}-r1/"
echo ""
echo "🔍 Manual Verification:"
echo "  1. Check GitHub for new repo"
echo "  2. Check GitHub Pages is live"
echo "  3. Verify stats show 2 processed tasks"
echo "  4. Confirm duplicate was rejected"
