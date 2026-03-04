from typing import Any
from app.interfaces.i_audit_repository import IAuditRepository


class AuditRepository(IAuditRepository):
    def __init__(self, db):
        self.collection = db["audit_logs"]

    async def create(self, doc: dict) -> Any:
        result = await self.collection.insert_one(doc)
        return result.inserted_id

    async def find_many(self, filters: dict, limit: int = 50) -> list:
        cursor = self.collection.find(filters).sort("timestamp", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs
