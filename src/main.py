from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.logger import RequestLoggingMiddleware, logger
from src.routers import api_keys, auth, user_data, scans, analytics
from src.services.event_handlers import register_events


# Register event bus listeners
register_events()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for KeySentry, handling API key detection and management.",
)

app.add_middleware(RequestLoggingMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        body = await request.json()
    except Exception:
        try:
            body = (await request.body()).decode("utf-8")
        except Exception:
            body = "<unreadable body>"
    logger.error(
        f"Validation error on {request.method} {request.url.path}: {exc.errors()} - Body: {body}"
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(
        f"HTTP error on {request.method} {request.url.path} - Status: {exc.status_code} - Detail: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(
        f"Unhandled exception on {request.method} {request.url.path}: {exc}"
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


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
