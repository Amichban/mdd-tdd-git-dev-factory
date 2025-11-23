.PHONY: help install dev up down build test lint generate clean deploy-vercel feedback

# Default target
help:
	@echo "Development Platform - Available Commands"
	@echo "=========================================="
	@echo ""
	@echo "  Setup & Install:"
	@echo "    make install      - Install all dependencies"
	@echo "    make setup        - Full setup (install + build + db)"
	@echo ""
	@echo "  Development:"
	@echo "    make dev          - Start all services for development"
	@echo "    make up           - Start all services (detached)"
	@echo "    make down         - Stop all services"
	@echo "    make logs         - View logs from all services"
	@echo "    make shell        - Open shell in backend container"
	@echo ""
	@echo "  Testing:"
	@echo "    make test         - Run all tests"
	@echo "    make test-watch   - Run tests in watch mode"
	@echo "    make coverage     - Run tests with coverage report"
	@echo ""
	@echo "  Code Quality:"
	@echo "    make lint         - Run linters (ruff, eslint)"
	@echo "    make format       - Format code"
	@echo "    make typecheck    - Run type checkers"
	@echo ""
	@echo "  Code Generation:"
	@echo "    make generate     - Generate code from specs"
	@echo "    make validate     - Validate specs against schema"
	@echo ""
	@echo "  Build & Deploy:"
	@echo "    make build        - Build Docker images"
	@echo "    make build-prod   - Build production images"
	@echo "    make deploy-vercel - Deploy frontend to Vercel"
	@echo ""
	@echo "  Database:"
	@echo "    make db-migrate   - Run database migrations"
	@echo "    make db-reset     - Reset database"
	@echo ""
	@echo "  Cleanup:"
	@echo "    make clean        - Remove all containers and volumes"

# ===========================================
# Setup & Install
# ===========================================

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	npm install
	@echo "✅ Dependencies installed"

setup: install
	@echo "🔧 Setting up development environment..."
	cp -n .env.example .env || true
	docker compose build
	docker compose up -d db redis
	sleep 5
	make db-migrate
	make generate
	@echo "✅ Setup complete! Run 'make dev' to start"

# ===========================================
# Development
# ===========================================

dev:
	@echo "🚀 Starting development environment..."
	docker compose up

up:
	@echo "🚀 Starting services (detached)..."
	docker compose up -d

down:
	@echo "🛑 Stopping services..."
	docker compose down

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

shell:
	docker compose exec backend /bin/bash

shell-db:
	docker compose exec db psql -U postgres -d quantx

# ===========================================
# Testing
# ===========================================

test:
	@echo "🧪 Running tests..."
	docker compose --profile test run --rm test

test-local:
	pytest tests/ -v --cov=src --cov-report=term-missing

test-watch:
	pytest tests/ -v --watch

coverage:
	@echo "📊 Running tests with coverage..."
	docker compose --profile test run --rm test pytest tests/ -v --cov=src --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

# ===========================================
# Code Quality
# ===========================================

lint:
	@echo "🔍 Running linters..."
	ruff check .
	npm run lint

format:
	@echo "✨ Formatting code..."
	ruff format .
	npx prettier --write "src/**/*.{ts,tsx,json}"

typecheck:
	@echo "🔎 Running type checkers..."
	mypy src generators --ignore-missing-imports
	npm run type-check

# ===========================================
# Code Generation
# ===========================================

generate:
	@echo "⚙️  Generating code from specs..."
	python generators/generate_all.py
	@echo "✅ Code generation complete"

validate:
	@echo "✅ Validating specs..."
	python generators/generate_all.py --validate-only

# ===========================================
# Build & Deploy
# ===========================================

build:
	@echo "🏗️  Building Docker images..."
	docker compose build

build-prod:
	@echo "🏗️  Building production images..."
	docker build -f backend.Dockerfile -t dev-platform-backend:latest .
	docker build -f frontend.Dockerfile -t dev-platform-frontend:latest .

deploy-vercel:
	@echo "🚀 Deploying frontend to Vercel..."
	cd src/app && npx vercel --prod

# ===========================================
# Database
# ===========================================

db-migrate:
	@echo "🗃️  Running database migrations..."
	docker compose exec backend alembic upgrade head

db-reset:
	@echo "⚠️  Resetting database..."
	docker compose down -v
	docker compose up -d db
	sleep 5
	make db-migrate

# ===========================================
# Cleanup
# ===========================================

clean:
	@echo "🧹 Cleaning up..."
	docker compose down -v --remove-orphans
	rm -rf node_modules
	rm -rf __pycache__ .pytest_cache .mypy_cache
	rm -rf .next
	rm -rf htmlcov coverage.xml
	@echo "✅ Cleanup complete"

# ===========================================
# Feedback
# ===========================================

feedback:
	@echo "📝 Adding feedback..."
	python scripts/add-feedback.py
