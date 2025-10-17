#!/bin/bash

# TDS Project 1 - Instructor Run Script

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please run ./scripts/setup_instructor.sh first"
    exit 1
fi

# Start the evaluation API
echo "🚀 Starting Evaluation API..."
cd instructor
python evaluation_api.py
