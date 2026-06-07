#!/usr/bin/env bash
# One-command hackathon startup (Unix/macOS/Git Bash)
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — add your API keys!"
fi

echo "Starting backend on :8000..."
(cd backend && uvicorn app:app --reload --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

echo "Starting frontend on :3000..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

echo ""
echo "✓ Backend:  http://localhost:8000/docs"
echo "✓ Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop"

wait
