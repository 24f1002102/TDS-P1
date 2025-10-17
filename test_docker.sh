#!/bin/bash

# Docker Test Script
echo "======================================"
echo "🐳 Docker Build & Test"
echo "======================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Build Docker Image
echo ""
echo "${BLUE}Step 1: Building Docker Image...${NC}"
echo "This will take 5-10 minutes on first build"
docker build -t tds-student-api:latest .

if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Docker image built successfully${NC}"
else
    echo "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Step 2: Check image size
echo ""
echo "${BLUE}Step 2: Checking Image Size${NC}"
docker images tds-student-api:latest

# Step 3: Run container
echo ""
echo "${BLUE}Step 3: Starting Container...${NC}"
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Container started${NC}"
else
    echo "${RED}❌ Container failed to start${NC}"
    exit 1
fi

# Step 4: Wait for container to be ready
echo ""
echo "${BLUE}Step 4: Waiting for API to be ready (30s)...${NC}"
sleep 10
echo "10 seconds..."
sleep 10
echo "20 seconds..."
sleep 10
echo "30 seconds..."

# Step 5: Check container logs
echo ""
echo "${BLUE}Step 5: Container Logs:${NC}"
docker-compose logs --tail=20

# Step 6: Test health endpoint
echo ""
echo "${BLUE}Step 6: Testing Health Endpoint${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
echo "Response: $HEALTH_RESPONSE"

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "${GREEN}✅ Health check passed${NC}"
else
    echo "${RED}❌ Health check failed${NC}"
    echo "Container logs:"
    docker-compose logs
    exit 1
fi

# Step 7: Test stats endpoint
echo ""
echo "${BLUE}Step 7: Testing Stats Endpoint${NC}"
curl -s http://localhost:8000/stats | jq .

if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Stats endpoint working${NC}"
else
    echo "${RED}❌ Stats endpoint failed${NC}"
fi

# Step 8: Test root endpoint
echo ""
echo "${BLUE}Step 8: Testing Root Endpoint${NC}"
curl -s http://localhost:8000/ | jq .

# Step 9: Check container health status
echo ""
echo "${BLUE}Step 9: Container Health Status${NC}"
docker ps --filter name=tds-student-api --format "table {{.Names}}\t{{.Status}}"

# Step 10: Test full task submission
echo ""
echo "${BLUE}Step 10: Testing Task Submission${NC}"
echo "Submitting test task..."

source .env
TEST_TASK="docker-test-$(date +%s)"
TEST_NONCE="nonce-$(date +%s)"

curl -X POST http://localhost:8000/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"${STUDENT_EMAIL}"'",
    "secret": "'"${STUDENT_SECRET}"'",
    "task": "'"${TEST_TASK}"'",
    "round": 1,
    "nonce": "'"${TEST_NONCE}"'",
    "brief": "Create a simple HTML page that displays Docker Test in a centered h1 tag with green background",
    "checks": ["Page displays Docker Test", "Background is green"],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }' | jq .

echo ""
echo "${GREEN}✅ Task submitted! Watch logs:${NC}"
echo "   ${YELLOW}docker-compose logs -f${NC}"

# Summary
echo ""
echo "======================================"
echo "${GREEN}Docker Test Complete!${NC}"
echo "======================================"
echo ""
echo "📊 Quick Commands:"
echo "   View logs:       docker-compose logs -f"
echo "   Stop container:  docker-compose down"
echo "   Restart:         docker-compose restart"
echo "   Shell access:    docker exec -it tds-student-api bash"
echo ""
echo "🌐 API Available at: http://localhost:8000"
echo "   Health:   http://localhost:8000/health"
echo "   Stats:    http://localhost:8000/stats"
echo "   API:      http://localhost:8000/api/task"
echo ""
echo "🔍 Check GitHub for repo: ${TEST_TASK}-r1"
echo "   Repo URL: https://github.com/${GITHUB_USERNAME}/${TEST_TASK}-r1"
echo "   Pages:    https://${GITHUB_USERNAME}.github.io/${TEST_TASK}-r1/"
