from datetime import datetime, timezone
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user_model import UserLogin, UserResponse
from app.models.token_model import TokenResponse
from app.core.exceptions import AuthError
from app.config import get_settings

settings = get_settings()


class AuthService:
    def __init__(self, user_repo, token_repo, audit_service):
        self.users = user_repo
        self.tokens = token_repo
        self.audit = audit_service

    async def login(self, data: UserLogin, ip: str, ua: str) -> TokenResponse:
        user = await self.users.find_by_username(data.username)
        if not user or not verify_password(data.password, user["hashed_password"]):
            await self.audit.log(
                "failed_login", None, data.username, ip, ua, False,
                {"reason": "Invalid credentials"},
            )
            raise AuthError("Invalid username or password")

        if not user.get("is_active", True):
            await self.audit.log(
                "failed_login", str(user["_id"]), user["username"], ip, ua, False,
                {"reason": "Account deactivated"},
            )
            raise AuthError("Account is deactivated")

        access_token, jti = create_access_token(str(user["_id"]))
        refresh_token, expires = create_refresh_token(str(user["_id"]))

        await self.tokens.store_refresh_token(str(user["_id"]), refresh_token, jti, expires)
        await self.users.update_last_login(str(user["_id"]))
        await self.audit.log("login", str(user["_id"]), user["username"], ip, ua, True, {})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    async def logout(self, jti: str, user_id: str, ip: str, ua: str) -> None:
        await self.tokens.revoke_token(jti)
        user = await self.users.find_by_id(user_id)
        username = user["username"] if user else "unknown"
        await self.audit.log("logout", user_id, username, ip, ua, True, {})

    async def refresh_token(self, refresh_token: str, ip: str, ua: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise AuthError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise AuthError("Not a refresh token")

        token_doc = await self.tokens.find_by_refresh_token(refresh_token)
        if not token_doc or token_doc["is_revoked"]:
            raise AuthError("Refresh token revoked or not found")

        user = await self.users.find_by_id(payload["sub"])
        if not user:
            raise AuthError("User not found")

        # Rotate tokens
        await self.tokens.revoke_token(token_doc["access_jti"])
        new_access, new_jti = create_access_token(str(user["_id"]))
        new_refresh, new_expires = create_refresh_token(str(user["_id"]))
        await self.tokens.store_refresh_token(
            str(user["_id"]), new_refresh, new_jti, new_expires
        )
        await self.audit.log(
            "token_refresh", str(user["_id"]), user["username"], ip, ua, True, {}
        )

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )
