from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import hash_password
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.models.response_model import ApiResponse

router = APIRouter(prefix="/api/internal", tags=["Internal"])

# All internal routes are admin-level — require a valid Bearer token in Swagger.
_bearer = HTTPBearer(auto_error=False)


# ── User creation model ───────────────────────────────────────────────────────
class CreateUserBody(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="alice")
    email: EmailStr = Field(..., example="alice@truedna.com")
    password: str = Field(..., min_length=8, example="Alice@1234")


# ── Users ─────────────────────────────────────────────────────────────────────
@router.post("/users", status_code=201)
async def create_user(
    body: CreateUserBody,
    db=Depends(get_db),
    _token: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """Create a user directly in the users collection (admin only)."""
    repo = UserRepository(db)

    if await repo.find_by_username(body.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    if await repo.find_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    doc = {
        "username": body.username,
        "email": body.email,
        "hashed_password": hash_password(body.password),
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "last_login": None,
    }
    result = await db["users"].insert_one(doc)
    return ApiResponse.ok(
        data={
            "user_id": str(result.inserted_id),
            "username": body.username,
            "email": body.email,
        },
        message="User created successfully",
        status_code=201,
    )


@router.get("/users")
async def list_all_users(
    db=Depends(get_db),
    _token: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """List all users from the users collection (admin only)."""
    repo = UserRepository(db)
    users = await repo.find_all(limit=200)
    data = [
        {
            "user_id": u["_id"],
            "username": u["username"],
            "email": u["email"],
            "is_active": u.get("is_active", True),
            "created_at": u.get("created_at"),
            "last_login": u.get("last_login"),
        }
        for u in users
    ]
    return ApiResponse.ok(data=data, message=f"{len(data)} user(s) retrieved")


# ── Audit logs ────────────────────────────────────────────────────────────────
@router.post("/audit")
async def create_audit_entry(
    body: dict,
    db=Depends(get_db),
    _token: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """Manually insert an audit log entry (admin only)."""
    repo = AuditRepository(db)
    result = await repo.create(body)
    return ApiResponse.ok(data={"inserted_id": str(result)}, message="Audit entry created")


@router.get("/audit")
async def get_audit_logs(
    event_type: str | None = Query(None),
    user_id: str | None = Query(None),
    limit: int = Query(50, le=200),
    db=Depends(get_db),
    _token: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """Query audit logs with optional filters (admin only)."""
    repo = AuditRepository(db)
    filters: dict = {}
    if event_type:
        filters["event_type"] = event_type
    if user_id:
        filters["user_id"] = user_id
    logs = await repo.find_many(filters, limit)
    return ApiResponse.ok(data=logs, message=f"{len(logs)} audit log(s) retrieved")


