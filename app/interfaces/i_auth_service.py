from abc import ABC, abstractmethod
from app.models.user_model import UserLogin
from app.models.token_model import TokenResponse


class IAuthService(ABC):
    @abstractmethod
    async def login(self, data: UserLogin, ip: str, ua: str) -> TokenResponse: ...

    @abstractmethod
    async def logout(self, jti: str, user_id: str, ip: str, ua: str) -> None: ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str, ip: str, ua: str) -> TokenResponse: ...
