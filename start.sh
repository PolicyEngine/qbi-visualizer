#!/bin/bash

# QBI Visualizer - local dev start script.
# Sets up and runs the backend (FastAPI, port 8000) and the frontend
# (Next.js via bun, port 3000 under /us/qbi-calculator).

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Backend setup
if [ ! -f "$ROOT/backend/.env" ] && [ -f "$ROOT/backend/.env.example" ]; then
    cp "$ROOT/backend/.env.example" "$ROOT/backend/.env"
    echo "Created backend/.env from .env.example"
fi

if [ ! -d "$ROOT/backend/venv" ]; then
    echo "Creating backend virtual environment..."
    python3 -m venv "$ROOT/backend/venv"
fi

echo "Installing backend dependencies..."
"$ROOT/backend/venv/bin/pip" install -q --upgrade pip
"$ROOT/backend/venv/bin/pip" install -q -e "$ROOT/backend"

# Frontend setup
if [ ! -d "$ROOT/frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    (cd "$ROOT/frontend" && bun install)
fi

echo ""
echo "Backend:  http://localhost:8000 (docs at /docs)"
echo "Frontend: http://localhost:3000/us/qbi-calculator"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

(cd "$ROOT/backend" && exec venv/bin/uvicorn app.main:app --reload --port 8000) &
BACKEND_PID=$!

sleep 2

(cd "$ROOT/frontend" && exec bun run dev) &
FRONTEND_PID=$!

cleanup() {
    echo ""
    echo "Stopping services..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

wait
