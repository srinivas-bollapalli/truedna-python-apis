import time
import uuid
import logging
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.database import get_db

logger = logging.getLogger("api")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start = time.time()

        logger.info(f"[{request_id}] --> {request.method} {request.url.path}")

        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000

        logger.info(
            f"[{request_id}] <-- {response.status_code} {duration_ms:.1f}ms"
        )

        # Non-blocking write to service_logs
        try:
            db = await get_db()
            user_id = getattr(request.state, "user_id", None)
            await db["service_logs"].insert_one({
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc),
            })
        except Exception as exc:
            logger.warning(f"Failed to write service log: {exc}")

        response.headers["X-Request-ID"] = request_id
        return response
