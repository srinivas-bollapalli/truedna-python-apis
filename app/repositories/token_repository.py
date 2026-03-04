from datetime import datetime, timezone
from typing import Optional
from app.interfaces.i_token_repository import ITokenRepository


class TokenRepository(ITokenRepository):
    def __init__(self, db):
        self.collection = db["tokens"]

    async def store_refresh_token(
        self, user_id: str, refresh_token: str, access_jti: str, expires_at: datetime
    ) -> None:
        doc = {
            "user_id": user_id,
            "refresh_token": refresh_token,
            "access_jti": access_jti,
            "is_revoked": False,
            "created_at": datetime.now(timezone.utc),
            "expires_at": expires_at,
            "revoked_at": None,
        }
        await self.collection.insert_one(doc)

    async def find_by_refresh_token(self, refresh_token: str) -> Optional[dict]:
        return await self.collection.find_one({"refresh_token": refresh_token})

    async def is_jti_revoked(self, jti: str) -> bool:
        doc = await self.collection.find_one({"access_jti": jti, "is_revoked": True})
        return doc is not None

    async def revoke_token(self, jti: str) -> None:
        await self.collection.update_one(
            {"access_jti": jti},
            {"$set": {"is_revoked": True, "revoked_at": datetime.now(timezone.utc)}},
        )
