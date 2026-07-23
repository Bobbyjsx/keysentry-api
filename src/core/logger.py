import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Configure logger
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
