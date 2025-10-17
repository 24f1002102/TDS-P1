#!/bin/bash
# Startup script for Evaluation API (Instructor)

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to project root
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found. Run: python3 -m venv venv"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Copy .env.example to .env and configure it"
    exit 1
fi

# Add project root to PYTHONPATH
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Initialize database if needed
echo "📊 Initializing database..."
python -c "from shared.database import init_db; init_db()" 2>/dev/null || echo "Database already initialized"

echo "🚀 Starting Evaluation API..."
echo "📂 Project root: $SCRIPT_DIR"
echo "🐍 Python path: $PYTHONPATH"
echo ""

# Run the API
python -m instructor.evaluation_api
