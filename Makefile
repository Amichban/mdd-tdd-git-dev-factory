.PHONY: help install dev up down build test lint generate compile compile-clean generate-types validate mcp-server spec-snapshot spec-bump clean deploy-vercel feedback architect validate-9box

# Default target
help:
	@echo "MDD TDD Git Dev Factory - Available Commands"
	@echo "============================================="
	@echo ""
	@echo "  Setup & Install:"
	@echo "    make install      - Install all dependencies"
	@echo "    make setup        - Full setup (install + build + db)"
	@echo "    make hooks        - Enable git hooks"
	@echo ""
	@echo "  Development:"
	@echo "    make dev          - Start all services for development"
	@echo "    make up           - Start all services (detached)"
	@echo "    make down         - Stop all services"
	@echo "    make logs         - View logs from all services"
	@echo "    make shell        - Open shell in backend container"
	@echo ""
	@echo "  9-Box Architecture:"
	@echo "    make architect    - Generate 9-box spec from user story"
	@echo "    make validate-9box - Validate architecture specs"
	@echo "    make graph        - Show business graph"
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
	@echo "    make compile      - Compile all specs (unified)"
	@echo "    make compile-clean - Clean and recompile all"
	@echo "    make generate-types - Generate TypeScript types"
	@echo "    make validate     - Validate specs against schema"
	@echo ""
	@echo "  MCP Server:"
	@echo "    make mcp-server   - Start MCP server for Claude"
	@echo ""
	@echo "  Versioning:"
	@echo "    make spec-snapshot - Create spec snapshot"
	@echo "    make spec-bump    - Bump spec version"
	@echo ""
	@echo "  GitHub Workflow:"
	@echo "    make issue        - Create GitHub issue"
	@echo "    make implement    - Implement from issue"
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
	@echo "  Kafka:"
	@echo "    make kafka-topics - Create Kafka topics"
	@echo "    make kafka-list   - List Kafka topics"
	@echo ""
	@echo "  Utilities:"
	@echo "    make feedback     - Add problems/enhancements"
	@echo "    make clean        - Remove all containers and volumes"

# ===========================================
# Setup & Install
# ===========================================

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	npm install
	@echo "✅ Dependencies installed"

setup: install hooks
	@echo "🔧 Setting up development environment..."
	cp -n .env.example .env || true
	docker compose build
	docker compose up -d db redis
	sleep 5
	make db-migrate
	make generate
	@echo "✅ Setup complete! Run 'make dev' to start"

hooks:
	@echo "🔗 Enabling git hooks..."
	git config core.hooksPath .githooks
	chmod +x .githooks/*
	@echo "✅ Git hooks enabled"

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
# 9-Box Architecture
# ===========================================

architect:
	@echo "🏗️  Generating 9-box architecture spec..."
	@read -p "Enter user story: " story; \
	claude @architect "$$story"

validate-9box:
	@echo "✅ Validating architecture specs..."
	@for f in specs/architecture/*.json; do \
		echo "  Checking $$f..."; \
		python -c "import json; json.load(open('$$f'))"; \
	done
	@echo "✅ All architecture specs valid"

graph:
	@echo "📊 Business Graph Nodes:"
	@find specs/architecture -name "*.json" -exec jq -r '.graph_nodes[]? | "  [\(.type)] \(.id) - \(.label)"' {} \; 2>/dev/null || echo "  No architecture specs found"

# ===========================================
# GitHub Workflow
# ===========================================

issue:
	@echo "📋 Creating GitHub issue..."
	gh issue create

implement:
	@echo "🚀 Implementing from issue..."
	@read -p "Enter issue number: " num; \
	python -c "from pathlib import Path; from services.orchestrator import Orchestrator; Orchestrator(Path('.')).implement_issue($$num)"

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

compile:
	@echo "⚙️  Compiling all specs..."
	python generators/compile_specs.py
	@echo "✅ Compilation complete"

compile-clean:
	@echo "🧹 Cleaning and recompiling..."
	python generators/compile_specs.py --clean --manifest
	@echo "✅ Clean compilation complete"

generate-types:
	@echo "⚙️  Generating TypeScript types..."
	python generators/generate_types.py
	@echo "✅ TypeScript types generated"

validate:
	@echo "✅ Validating specs..."
	python generators/generate_all.py --validate-only

# ===========================================
# MCP Server
# ===========================================

mcp-server:
	@echo "🤖 Starting MCP server..."
	python mcp/server.py

# ===========================================
# Versioning
# ===========================================

spec-snapshot:
	@echo "📸 Creating spec snapshot..."
	@read -p "Spec type (entities/workflows/algorithms): " type; \
	read -p "Label (optional): " label; \
	python -c "from services.spec_versioning import create_snapshot; print(create_snapshot('$$type', '$$label' or None))"

spec-bump:
	@echo "📈 Bumping spec version..."
	@read -p "Spec type: " type; \
	read -p "Bump (major/minor/patch): " part; \
	python -c "from services.spec_versioning import bump_version; print(bump_version('$$type', '$$part'))"

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
# Kafka
# ===========================================

kafka-topics:
	@echo "📨 Creating Kafka topics..."
	python -c "from services.kafka_service import init_kafka_topics; init_kafka_topics()"
	@echo "✅ Kafka topics created"

kafka-list:
	@echo "📋 Listing Kafka topics..."
	docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

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
