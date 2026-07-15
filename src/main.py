from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.routers import api_keys, auth, user_data, scans, analytics
from src.services.event_handlers import register_events

# Register event bus listeners
register_events()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for KeySentry, handling API key detection and management.",
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
