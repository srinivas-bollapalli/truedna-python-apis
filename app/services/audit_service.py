from datetime import datetime, timezone


class AuditService:
    def __init__(self, audit_repo):
        self.repo = audit_repo

    async def log(
        self,
        event_type: str,
        user_id: str | None,
        username: str | None,
        ip_address: str,
        user_agent: str,
        success: bool,
        details: dict,
    ) -> None:
        doc = {
            "event_type": event_type,
            "user_id": user_id,
            "username": username,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "details": details,
            "timestamp": datetime.now(timezone.utc),
        }
        await self.repo.create(doc)
