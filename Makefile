.PHONY: help install backend frontend dev docker test clean setup

help:
	@echo "Monad Agent Hackathon Kit"
	@echo ""
	@echo "  make setup     - Copy .env.example and install all deps"
	@echo "  make install   - Install backend + frontend dependencies"
	@echo "  make backend   - Start FastAPI backend (port 8000)"
	@echo "  make frontend  - Start Next.js frontend (port 3000)"
	@echo "  make dev       - Start both (requires two terminals or use docker)"
	@echo "  make docker    - Start with Docker Compose"
	@echo "  make test      - Run backend tests"
	@echo "  make clean     - Remove caches and node_modules"

setup:
	cp -n .env.example .env 2>/dev/null || copy .env.example .env
	$(MAKE) install

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && uvicorn app:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

docker:
	docker compose up --build

test:
	cd backend && python -m pytest ../tests/ -v

clean:
	rm -rf frontend/node_modules frontend/.next
	rm -rf backend/__pycache__ backend/**/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
