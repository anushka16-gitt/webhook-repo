#!/bin/bash

# Start script for GitHub Webhook Monitor
# This script starts both Flask backend and Streamlit frontend

echo "=================================="
echo "GitHub Webhook Monitor"
echo "=================================="
echo ""

# Check if MongoDB is running
echo "Checking MongoDB connection..."
if ! mongosh --eval "db.runCommand({ ping: 1 })" > /dev/null 2>&1; then
    echo "⚠️  MongoDB is not running!"
    echo "Please start MongoDB first:"
    echo "  - Mac: brew services start mongodb-community"
    echo "  - Linux: sudo systemctl start mongod"
    echo "  - Windows: net start MongoDB"
    exit 1
fi
echo "✅ MongoDB is running"
echo ""

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
pip install -q -r requirements.txt

# Start Flask in background
echo ""
echo "Starting Flask backend on port 5000..."
python run.py > flask.log 2>&1 &
FLASK_PID=$!
echo "Flask PID: $FLASK_PID"

# Wait for Flask to start
sleep 3

# Check if Flask started successfully
if ! curl -s http://localhost:5000/webhook/health > /dev/null; then
    echo "❌ Flask failed to start. Check flask.log for errors."
    kill $FLASK_PID 2>/dev/null
    exit 1
fi
echo "✅ Flask backend is running"

# Start Streamlit
echo ""
echo "Starting Streamlit UI on port 8501..."
echo ""
echo "=================================="
echo "Access the application:"
echo "  - Flask API: http://localhost:5000"
echo "  - Streamlit UI: http://localhost:8501"
echo "=================================="
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Trap Ctrl+C to kill both processes
trap "echo ''; echo 'Stopping services...'; kill $FLASK_PID 2>/dev/null; exit 0" INT

# Start Streamlit (this will block until stopped)
streamlit run ui.py

# Cleanup
kill $FLASK_PID 2>/dev/null
