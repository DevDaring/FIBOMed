#!/bin/bash
# run.sh - Unix/Linux/Mac script to run FIBOMed
# Loads environment from secrets/.env and starts both backend and frontend servers

set -e

echo "============================================"
echo "   FIBOMed - Medical Visual Storytelling"
echo "============================================"
echo ""

# Check if secrets/.env exists
if [ ! -f "secrets/.env" ]; then
    echo "ERROR: secrets/.env file not found!"
    echo "Please create secrets/.env with required environment variables."
    echo "See .env.example for reference."
    exit 1
fi

echo "[1/5] Loading environment variables from secrets/.env..."
set -a
source secrets/.env
set +a
echo "      Environment variables loaded."
echo ""

echo "[2/5] Creating data directories..."
mkdir -p data/csv_files
mkdir -p data/generated/audio
mkdir -p data/generated/prompts
mkdir -p data/generated/visualizations
mkdir -p data/uploads/audio
echo "      Data directories ready."
echo ""

echo "[3/5] Setting up Python virtual environment..."
if [ ! -d "backend/venv" ]; then
    echo "      Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi
echo "      Virtual environment ready."
echo ""

echo "[4/5] Starting Backend Server..."
(cd backend && source venv/bin/activate && pip install -r requirements.txt -q && python main.py) &
BACKEND_PID=$!
echo "      Backend starting on http://localhost:8000 (PID: $BACKEND_PID)"
echo ""

# Wait for backend to initialize
echo "      Waiting for backend to initialize..."
sleep 5

echo "[5/5] Starting Frontend Development Server..."
(cd frontend && npm install && npm run dev) &
FRONTEND_PID=$!
echo "      Frontend starting on http://localhost:5173 (PID: $FRONTEND_PID)"
echo ""

echo "============================================"
echo "   FIBOMed Services Started!"
echo "============================================"
echo ""
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Frontend:     http://localhost:5173"
echo ""
echo "   Press Ctrl+C to stop all services"
echo "============================================"
echo ""

# Trap Ctrl+C to kill both processes
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "Services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait
