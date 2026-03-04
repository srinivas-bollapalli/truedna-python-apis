from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from app.interfaces.i_user_repository import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, db):
        self.collection = db["users"]

    async def find_by_username(self, username: str) -> Optional[dict]:
        return await self.collection.find_one({"username": username})

    async def find_by_email(self, email: str) -> Optional[dict]:
        return await self.collection.find_one({"email": email})

    async def find_by_id(self, user_id: str) -> Optional[dict]:
        try:
            return await self.collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None

    async def find_all(self, limit: int = 100) -> list:
        cursor = self.collection.find({}).limit(limit)
        docs = await cursor.to_list(length=limit)
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs

    async def update_last_login(self, user_id: str) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}},
        )
