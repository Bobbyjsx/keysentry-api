.PHONY: install dev worker clean init-db lint lint-fix

# Variables
PYTHON = .venv/bin/python
UVICORN = .venv/bin/uvicorn
CELERY = .venv/bin/celery
PIP = .venv/bin/pip

install:
	@echo "Creating virtual environment and installing dependencies..."
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

dev:
	@echo "Starting FastAPI development server..."
	$(UVICORN) src.main:app --reload --host 127.0.0.1 --port 8000

worker:
	@echo "Starting Celery background worker..."
	$(CELERY) -A src.worker.celery_app worker --loglevel=info

init-db:
	@echo "Initializing database schema..."
	$(PYTHON) init_db.py

lint:
	@echo "Running Ruff linter..."
	.venv/bin/ruff check .
	@echo "Running Ruff formatter check..."
	.venv/bin/ruff format --check .

lint-fix:
	@echo "Formatting and fixing code with Ruff..."
	.venv/bin/ruff check --fix .
	.venv/bin/ruff format .

clean:
	@echo "Cleaning up python cache files..."
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
