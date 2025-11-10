#!/bin/bash

echo "🚀 The Climb - Starting Application"
echo "==================================="
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env file not found!"
    echo ""
    echo "Please create it from .env.example and add your keys:"
    echo "  cd backend"
    echo "  cp .env.example .env"
    echo "  # Edit .env with your API keys"
    echo ""
    exit 1
fi

echo "✅ Environment file found"
echo ""

# Start backend
echo "📦 Starting Backend (FastAPI)..."
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

echo ""

# Start frontend
echo "🎨 Starting Frontend (React + Vite)..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Application started!"
echo ""
echo "🌐 Open your browser to: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Keep script running
wait
