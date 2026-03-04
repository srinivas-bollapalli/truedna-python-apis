from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, ExpiredSignatureError
from app.core.security import decode_token
from app.core.database import get_db
from app.repositories.token_repository import TokenRepository

# Paths that do NOT require a JWT
EXCLUDED_PATHS = [
    "/api/auth/",
    "/api/health",
    "/api/internal/",
    "/docs",
    "/redoc",
    "/openapi.json",
]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Always allow excluded paths
        if any(path.startswith(p) for p in EXCLUDED_PATHS):
            return await call_next(request)

        # All other paths require a valid access token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Missing authentication token"}, status_code=401)

        token = auth_header.split(" ", 1)[1]

        try:
            payload = decode_token(token)
        except ExpiredSignatureError:
            return JSONResponse({"detail": "Token has expired"}, status_code=401)
        except JWTError:
            return JSONResponse({"detail": "Invalid token signature"}, status_code=401)

        if payload.get("type") != "access":
            return JSONResponse({"detail": "Invalid token type"}, status_code=401)

        # Check blacklist
        db = await get_db()
        token_repo = TokenRepository(db)
        if await token_repo.is_jti_revoked(payload["jti"]):
            return JSONResponse({"detail": "Token has been revoked"}, status_code=401)

        # Attach user info for downstream handlers
        request.state.user_id = payload["sub"]
        request.state.jti = payload["jti"]

        return await call_next(request)
