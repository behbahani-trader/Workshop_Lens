.PHONY: help install test lint format clean build run docker-build docker-run

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linters"
	@echo "  make format    - Format code"
	@echo "  make clean     - Clean up"
	@echo "  make build     - Build static files"
	@echo "  make run       - Run the application"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	npm install

test:
	pytest

lint:
	flake8 app tests
	black --check app tests
	isort --check-only app tests
	mypy app

format:
	black app tests
	isort app tests

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".tox" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name "dist" -exec rm -r {} +
	find . -type d -name "build" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "coverage.xml" -exec rm -r {} +
	find . -type d -name "*.cover" -exec rm -r {} +
	find . -type d -name ".hypothesis" -exec rm -r {} +
	find . -type d -name "docs/_build" -exec rm -r {} +
	find . -type d -name "site" -exec rm -r {} +
	find . -type d -name "node_modules" -exec rm -r {} +
	find . -type f -name "npm-debug.log*" -delete
	find . -type f -name "yarn-debug.log*" -delete
	find . -type f -name "yarn-error.log*" -delete

build:
	npm run build

run:
	python app.py

docker-build:
	docker-compose build

docker-run:
	docker-compose up 