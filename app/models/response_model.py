"""
Standard API response envelope used by every endpoint in this project.

Shape:
{
    "success": true | false,
    "statusCode": 200,
    "message": "Human-readable description",
    "data": { ... } | null,
    "timestamp": "2026-03-03T12:00:00.000Z"
}
"""
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel
from datetime import datetime, timezone

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    statusCode: int
    message: str
    data: Optional[T] = None
    timestamp: str

    @classmethod
    def ok(
        cls,
        data: Any = None,
        message: str = "Request successful",
        status_code: int = 200,
    ) -> "ApiResponse":
        return cls(
            success=True,
            statusCode=status_code,
            message=message,
            data=data,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def error(
        cls,
        message: str = "An error occurred",
        status_code: int = 400,
        data: Any = None,
    ) -> "ApiResponse":
        return cls(
            success=False,
            statusCode=status_code,
            message=message,
            data=data,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
