from abc import ABC, abstractmethod
from typing import Optional


class IUserRepository(ABC):
    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[dict]: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[dict]: ...

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[dict]: ...

    @abstractmethod
    async def update_last_login(self, user_id: str) -> None: ...
