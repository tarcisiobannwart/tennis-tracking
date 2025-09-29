#!/bin/bash

# Tennis Tracking API Start Script

set -e

echo "🎾 Starting Tennis Tracking API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads temp output logs

# Download YOLO weights if not present
YOLO_WEIGHTS="../Yolov3/yolov3.weights"
if [ ! -f "$YOLO_WEIGHTS" ]; then
    echo "Downloading YOLO weights (237MB)..."
    mkdir -p ../Yolov3
    wget -O "$YOLO_WEIGHTS" https://pjreddie.com/media/files/yolov3.weights
fi

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "🚀 Starting API server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload