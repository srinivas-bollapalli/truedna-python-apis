from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user_model import UserLogin
from app.models.token_model import TokenResponse, RefreshRequest
from app.models.response_model import ApiResponse
from app.services.auth_service import AuthService
from app.dependencies import get_auth_service
from app.core.exceptions import AuthError
from app.core.security import decode_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Swagger-only: makes Swagger show 🔒 on routes that require a token.
# Actual JWT validation is done by AuthMiddleware / endpoint logic.
_bearer = HTTPBearer(auto_error=False)


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(
    data: UserLogin,
    request: Request,
    svc: AuthService = Depends(get_auth_service),
):
    """Authenticate with username + password. Returns access & refresh tokens."""
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    try:
        tokens = await svc.login(data, ip, ua)
        return ApiResponse.ok(data=tokens, message="Login successful")
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
async def logout(
    request: Request,
    svc: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
):
    """Revoke the current access token (adds jti to revocation list).
    Requires: `Authorization: Bearer <access_token>`"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    await svc.logout(payload["jti"], payload["sub"], ip, ua)
    return ApiResponse.ok(data=None, message="Logged out successfully")


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh(
    body: RefreshRequest,
    request: Request,
    svc: AuthService = Depends(get_auth_service),
):
    """Exchange a valid refresh token for a new token pair (rotates the refresh token)."""
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    try:
        tokens = await svc.refresh_token(body.refresh_token, ip, ua)
        return ApiResponse.ok(data=tokens, message="Token refreshed successfully")
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
