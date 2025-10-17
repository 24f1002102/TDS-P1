#!/bin/bash

# TDS Project 1 - Instructor Setup Script

echo "=== TDS Project 1: Instructor Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 not found"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Copy environment template
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your actual credentials"
else
    echo ".env already exists, skipping..."
fi

# Initialize database
echo "Initializing database..."
python3 -c "from shared.database import init_db; init_db()"

# Create necessary directories
echo "Creating directories..."
mkdir -p logs

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials:"
echo "   - OPENAI_API_KEY or ANTHROPIC_API_KEY"
echo "   - DATABASE_URL (if using PostgreSQL)"
echo "   - EVALUATION_API_URL"
echo ""
echo "2. Deploy evaluation API:"
echo "   cd instructor && python evaluation_api.py"
echo ""
echo "3. Collect student submissions (CSV)"
echo ""
echo "4. Send Round 1 tasks:"
echo "   python instructor/round1.py submissions.csv <eval-api-url>"
echo ""
echo "5. Evaluate submissions:"
echo "   python instructor/evaluate.py"
echo ""
echo "6. Send Round 2 tasks:"
echo "   python instructor/round2.py"
echo ""
