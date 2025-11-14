#!/bin/bash

# FIBOMed Setup Script
echo "=========================================="
echo "FIBOMed - Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✓ Python and Node.js found"
echo ""

# Backend setup
echo "Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

cd ..

# Frontend setup
echo ""
echo "Setting up frontend..."
cd frontend

# Install Node dependencies
echo "Installing Node dependencies..."
npm install

cd ..

# Initialize CSV database
echo ""
echo "Initializing CSV database..."
python3 scripts/init_csv.py

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit the .env file and add your API keys!"
fi

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Start the backend: cd backend && source venv/bin/activate && python main.py"
echo "3. Start the frontend (in a new terminal): cd frontend && npm run dev"
echo ""
