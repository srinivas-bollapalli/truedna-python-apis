from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class AuditLogResponse(BaseModel):
    event_type: str
    user_id: Optional[str]
    username: Optional[str]
    ip_address: str
    user_agent: str
    success: bool
    details: dict
    timestamp: datetime
