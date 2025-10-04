# Medical RAG Assistant Makefile
# Simple commands for development and deployment

.PHONY: help install setup test lint format clean run-api run-web docker-up docker-down

# Default target
help:
	@echo "Medical RAG Assistant - Available Commands:"
	@echo "=========================================="
	@echo "SETUP:"
	@echo "  make install     - Install all dependencies"
	@echo "  make setup       - Complete project setup"
	@echo ""
	@echo "QUALITY:"
	@echo "  make lint        - Run code linting (flake8)"
	@echo "  make format      - Format code (black + isort)"
	@echo "  make test        - Run all tests"
	@echo "  make check       - Run all quality checks"
	@echo ""
	@echo "RUN:"
	@echo "  make run-api     - Start FastAPI server"
	@echo "  make run-web     - Start Streamlit interface"
	@echo ""
	@echo "DOCKER:"
	@echo "  make docker-up   - Start all services with Docker"
	@echo "  make docker-down - Stop all Docker services"
	@echo "  make docker-logs - View Docker logs"
	@echo ""
	@echo "MAINTENANCE:"
	@echo "  make clean       - Clean temporary files"
	@echo "  make reset       - Reset development environment"

# Installation and Setup
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	pip install -e .

setup: install
	@echo "Setting up development environment..."
	pre-commit install
	@if [ ! -f .env ]; then \
		echo "Creating .env file from template..."; \
		cp .env.example .env; \
		echo "Please edit .env file with your API keys"; \
	fi
	@echo "Setup complete!"

# Code Quality
lint:
	@echo "Running linting..."
	flake8 medical_assistant_rag/ --count --show-source --statistics

format:
	@echo "Formatting code..."
	black medical_assistant_rag/
	isort medical_assistant_rag/

test:
	@echo "Running tests..."
	pytest -v

check: lint test
	@echo "All quality checks passed!"

# Running Applications
run-api:
	@echo "Starting FastAPI server..."
	PYTHONPATH=. python -m uvicorn src.api.main_api:app --reload --host 0.0.0.0 --port 8000

run-web:
	@echo "Starting Streamlit interface..."
	PYTHONPATH=. streamlit run src/api/web_interface.py

# Docker Operations
docker-up:
	@echo "Starting Docker services..."
	cd config && docker-compose up -d
	@echo "Services started! Check docker-compose ps"

docker-down:
	@echo "Stopping Docker services..."
	cd config && docker-compose down

docker-logs:
	@echo "Viewing Docker logs..."
	cd config && docker-compose logs -f

docker-build:
	@echo "Building Docker images..."
	cd config && docker-compose build

# Data Operations
ingest-data:
	@echo "Ingesting medical data..."
	PYTHONPATH=. python scripts/ingest.py

prepare-db:
	@echo "Preparing database..."
	PYTHONPATH=. python scripts/db_prep.py

# Maintenance
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type f -name ".coverage" -delete

reset: clean
	@echo "Resetting development environment..."
	docker-compose down -v
	rm -rf qdrant_storage/
	@echo "Environment reset complete!"

# Development helpers
dev-setup: setup
	@echo "Setting up for development..."
	pre-commit run --all-files || true
	@echo "Development environment ready!"

quick-check:
	@echo "Quick quality check..."
	black --check medical_assistant_rag/
	isort --check-only medical_assistant_rag/
	flake8 medical_assistant_rag/ --count --statistics

# Production helpers
prod-check: check
	@echo "Production readiness check..."
	@echo "Code quality: PASSED"
	@echo "Tests: PASSED"
	@echo "Ready for deployment!"