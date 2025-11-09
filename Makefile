.PHONY: help install install-dev build test lint format clean run docker-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make build         - Build the project"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make run           - Run the application"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

build:
	pip install -e .

test:
	pytest tests/ -v --cov=src/shiftly --cov-report=html --cov-report=term

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	ruff check --fix src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	uvicorn shiftly.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
