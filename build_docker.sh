#!/bin/bash

echo "🐳 Building Docker image..."
echo "This may take 5-10 minutes on first build..."
echo ""

docker build -t tds-student-api:latest .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    docker images tds-student-api:latest
    echo ""
    echo "Next steps:"
    echo "  1. Test locally:  docker-compose up"
    echo "  2. View logs:     docker-compose logs -f"
    echo "  3. Stop:          docker-compose down"
else
    echo ""
    echo "❌ Build failed!"
    exit 1
fi
