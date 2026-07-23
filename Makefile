.PHONY: install dev worker clean init-db lint lint-fix db-create db-up db-downgrade

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

db-create:
	@if [ -z "$(m)" ]; then echo "Migration message is required. Usage: make db-create m=\"message\""; exit 1; fi
	@echo "Creating new Alembic migration: $(m)..."
	.venv/bin/alembic revision --autogenerate -m "$(m)"

db-up:
	@echo "Upgrading database to latest migration..."
	.venv/bin/alembic upgrade head

db-downgrade:
	@echo "Downgrading database by one migration..."
	.venv/bin/alembic downgrade -1

lint:
	@echo "Running Ruff linter..."
	.venv/bin/ruff check .
	@echo "Running Ruff formatter check..."
	.venv/bin/ruff format --check .
	@echo "Running Pyright type checker..."
	npx pyright

lint-fix:
	@echo "Formatting and fixing code with Ruff..."
	.venv/bin/ruff check --fix .
	.venv/bin/ruff format .
	@echo "Running Pyright type checker..."
	npx pyright

clean:
	@echo "Cleaning up python cache files..."
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
