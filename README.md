# KeySentry API

KeySentry API is a backend Python service built on [FastAPI](https://fastapi.tiangolo.com/), designed to handle API key detection reporting and management.

This service abstracts the API layer previously coupled with the Next.js frontend, following proper API rules and SOLID principles.

## Features

- **FastAPI Framework**: High performance, easy-to-use, automatic OpenAPI documentation.
- **SOLID Principles**: Clean architecture utilizing the Repository Pattern and Dependency Injection.
- **Race Condition Prevention**: Uses PostgreSQL Row-Level Locks (`SELECT ... FOR UPDATE`) via SQLAlchemy when performing status updates.
- **Database Abstraction**: Fully async SQLAlchemy integration with `asyncpg` to interface with the KeySentry Supabase PostgreSQL instance.

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
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Set environment variables (or rely on defaults in `core/config.py`):
   ```bash
   export DATABASE_URL="postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres"
   ```

3. Run the development server:
   ```bash
   uvicorn src.main:app --reload
   ```

4. View API Documentation:
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
│   └── main.py         # Application factory and entry point
├── requirements.txt    # Project dependencies
└── README.md
```
