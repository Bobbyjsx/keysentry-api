from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.core.config import settings
from src.routers import api_keys, auth, user_data, scans, analytics
from src.services.event_handlers import register_events

logger = logging.getLogger("keysentry.api")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"Completed request: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.4f}s"
        )
        return response


# Register event bus listeners
register_events()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for KeySentry, handling API key detection and management.",
)

app.add_middleware(RequestLoggingMiddleware)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(api_keys.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(user_data.router, prefix=settings.API_V1_STR)
app.include_router(scans.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for the KeySentry API.
    """
    return {"status": "healthy", "service": settings.PROJECT_NAME}


# For running separately:
# uvicorn src.main:app --host 0.0.0.0 --port 8000
