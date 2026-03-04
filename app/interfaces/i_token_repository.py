from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class ITokenRepository(ABC):
    @abstractmethod
    async def store_refresh_token(
        self, user_id: str, refresh_token: str, access_jti: str, expires_at: datetime
    ) -> None: ...

    @abstractmethod
    async def find_by_refresh_token(self, refresh_token: str) -> Optional[dict]: ...

    @abstractmethod
    async def is_jti_revoked(self, jti: str) -> bool: ...

    @abstractmethod
    async def revoke_token(self, jti: str) -> None: ...
