from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.models.user_model import UserResponse
from app.models.response_model import ApiResponse

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

# Used purely for Swagger UI to display the 🔒 lock icon on protected routes.
# The actual JWT validation is performed by AuthMiddleware.
_bearer = HTTPBearer(auto_error=False)


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(
    request: Request,
    db=Depends(get_db),
    _token: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """Return the profile of the currently authenticated user."""
    user_id = request.state.user_id
    repo = UserRepository(db)
    user = await repo.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        is_active=user.get("is_active", True),
        created_at=user["created_at"],
        last_login=user.get("last_login"),
    )
    return ApiResponse.ok(data=data, message="User retrieved successfully")


@router.get("/", response_model=ApiResponse[list[UserResponse]])
async def list_users(
    db=Depends(get_db),
    _token: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """List all users (requires authentication — enforced by middleware)."""
    repo = UserRepository(db)
    users = await repo.find_all(limit=100)
    data = [
        UserResponse(
            id=u["_id"],
            username=u["username"],
            email=u["email"],
            is_active=u.get("is_active", True),
            created_at=u["created_at"],
            last_login=u.get("last_login"),
        )
        for u in users
    ]
    return ApiResponse.ok(data=data, message=f"{len(data)} user(s) retrieved")


@router.get("/{user_id}", response_model=ApiResponse[UserResponse])
async def get_user_by_id(
    user_id: str,
    db=Depends(get_db),
    _token: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """Get a specific user by their MongoDB ObjectId."""
    repo = UserRepository(db)
    user = await repo.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        is_active=user.get("is_active", True),
        created_at=user["created_at"],
        last_login=user.get("last_login"),
    )
    return ApiResponse.ok(data=data, message="User retrieved successfully")
