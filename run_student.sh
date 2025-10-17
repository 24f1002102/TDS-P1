#!/bin/bash

# TDS Project 1 - Student Run Script

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please run ./scripts/setup_student.sh first"
    exit 1
fi

# Start the API
echo "🚀 Starting Student API..."
cd student
python api.py
