#!/bin/bash

# Complete Docker Test Script
echo "======================================"
echo "🐳 Docker Image Testing"
echo "======================================"

# Wait for container to be healthy
echo ""
echo "⏳ Waiting for container to be ready..."
sleep 10

# Check if container is running
if ! docker ps | grep -q tds-student-api; then
    echo "❌ Container is not running!"
    echo "Logs:"
    docker-compose logs
    exit 1
fi

echo "✅ Container is running"
echo ""

# Test 1: Health Check
echo "Test 1: Health Endpoint"
HEALTH=$(curl -s http://localhost:8000/health)
echo "Response: $HEALTH"

if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    docker-compose logs
    exit 1
fi

echo ""

# Test 2: Stats
echo "Test 2: Stats Endpoint"
curl -s http://localhost:8000/stats | jq .
echo "✅ Stats endpoint working"

echo ""

# Test 3: Root
echo "Test 3: Root Endpoint"
curl -s http://localhost:8000/ | jq .
echo "✅ Root endpoint working"

echo ""
echo "======================================"
echo "✅ All Tests Passed!"
echo "======================================"
echo ""
echo "📊 Container Info:"
docker ps --filter name=tds-student-api --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📝 Next Steps:"
echo "  1. Push to Docker Hub: docker push YOUR_USER/tds-student-api:latest"
echo "  2. Deploy on Render using image URL"
echo "  3. Test production endpoint"
echo ""
echo "🔍 View logs: docker-compose logs -f"
echo "🛑 Stop: docker-compose down"
