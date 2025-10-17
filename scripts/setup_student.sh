#!/bin/bash

# TDS Project 1 - Student Setup Script

echo "=== TDS Project 1: Student Setup ==="
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

# Copy environment template
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your actual credentials"
else
    echo ".env already exists, skipping..."
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p generated_repos

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials:"
echo "   - STUDENT_SECRET"
echo "   - STUDENT_EMAIL"
echo "   - GITHUB_TOKEN"
echo "   - GITHUB_USERNAME"
echo "   - OPENAI_API_KEY or ANTHROPIC_API_KEY"
echo ""
echo "2. Start the API server:"
echo "   cd student && python api.py"
echo ""
echo "3. Expose your endpoint with ngrok:"
echo "   ngrok http 8000"
echo ""
echo "4. Submit your endpoint URL to the instructor"
echo ""
