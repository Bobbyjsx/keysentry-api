# KeySentry API

KeySentry API is a backend Python service built on [FastAPI](https://fastapi.tiangolo.com/), designed to handle API key detection reporting and management.

This service abstracts the API layer previously coupled with the Next.js frontend, following proper API rules and SOLID principles.

## Features

- **FastAPI Framework**: High performance, easy-to-use, automatic OpenAPI documentation.
- **SOLID Principles**: Clean architecture utilizing the Repository Pattern and Dependency Injection.
- **Race Condition Prevention**: Uses PostgreSQL Row-Level Locks (`SELECT ... FOR UPDATE`) via SQLAlchemy when performing status updates.
- **Database Abstraction**: Fully async SQLAlchemy integration with `asyncpg` to interface with the KeySentry Supabase PostgreSQL instance. Includes robust foreign key architecture tied directly to `profiles.id` allowing for "ghost users" without tight coupling to `auth.users`.
- **Advanced Secret Scanning**: Built-in GitHub scanning engine that dynamically fetches and validates regex patterns directly from the official Gitleaks registry for real-time security checking.
- **Background Task Processing**: Utilizes Celery with Redis for asynchronous processing of long-running Git repository scans.

## Deployment Strategies

This API is designed to be highly flexible for deployment:

### 1. Standalone Deployment
You can run this application completely standalone.

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 2. Integration with Project Atlas
This service can be easily integrated into the "Project Atlas" unified gateway. Since it exposes a standard ASGI `app` object in `src.main`, the Atlas Gateway can mount it directly:

```python
from src.main import app as keysentry_app
gateway_app.mount("/keysentry", keysentry_app)
```

## Setup & Local Development

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Set environment variables (or copy from `.env.example`):
   ```bash
   cp .env.example .env
   # Update DATABASE_URL with your Supabase credentials (e.g. Supavisor pooler on port 5432)
   ```

3. Ensure Redis is running for Celery:
   ```bash
   redis-server
   ```

4. Run the Celery worker (in a separate terminal):
   ```bash
   celery -A src.worker.celery_app worker --loglevel=info
   ```

5. Run the FastAPI development server:
   ```bash
   uvicorn src.main:app --reload
   ```

6. View API Documentation:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Project Structure

```text
keysentry-api/
├── src/
│   ├── core/           # Configuration and Database setup
│   ├── models/         # SQLAlchemy ORM models (mapping to DB schemas)
│   ├── schemas/        # Pydantic validation schemas
│   ├── repositories/   # Data Access Layer (SOLID)
│   ├── services/       # Business Logic Layer (SOLID)
│   ├── routers/        # FastAPI endpoint definitions
│   ├── worker/         # Celery background workers and tasks
│   ├── lib/            # External integrations (e.g. git_engine.py using Gitleaks)
│   └── main.py         # Application factory and entry point
├── requirements.txt    # Project dependencies
└── README.md
```
