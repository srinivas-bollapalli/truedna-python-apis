from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.models.response_model import ApiResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health", response_model=ApiResponse[dict])
async def health_check(db=Depends(get_db)):
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    data = {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "collections": ["users", "tokens", "audit_logs", "service_logs"],
    }
    return ApiResponse.ok(data=data, message="Health check successful")
