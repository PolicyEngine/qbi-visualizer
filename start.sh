#!/bin/bash

# QBI Visualizer - Quick Start Script
# This script sets up and runs both backend and frontend

set -e

echo "🚀 QBI Visualizer - Quick Start"
echo "================================"
echo ""

# Check if this is first run
if [ ! -f "backend/.env" ]; then
    echo "📝 First run detected - setting up configuration..."
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env"
fi

# Backend setup
echo ""
echo "🐍 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -e .

echo "✓ Backend setup complete"

cd ..

# Frontend setup
echo ""
echo "⚛️  Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
    echo "✓ Frontend setup complete"
else
    echo "✓ Dependencies already installed"
fi

cd ..

# Start services
echo ""
echo "🎬 Starting services..."
echo ""
echo "Backend will run on: http://localhost:8000"
echo "Frontend will run on: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Create a temporary script to run backend
cat > /tmp/qbi-backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
echo "🐍 Starting backend..."
python -m app.main
EOF

chmod +x /tmp/qbi-backend.sh

# Create a temporary script to run frontend
cat > /tmp/qbi-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
echo "⚛️  Starting frontend..."
npm run dev
EOF

chmod +x /tmp/qbi-frontend.sh

# Run both in background and capture PIDs
/tmp/qbi-backend.sh &
BACKEND_PID=$!

sleep 3

/tmp/qbi-frontend.sh &
FRONTEND_PID=$!

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    rm -f /tmp/qbi-backend.sh /tmp/qbi-frontend.sh
    echo "✓ Services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Wait for both processes
wait
