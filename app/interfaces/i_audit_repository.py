from abc import ABC, abstractmethod


class IAuditRepository(ABC):
    @abstractmethod
    async def create(self, doc: dict): ...

    @abstractmethod
    async def find_many(self, filters: dict, limit: int) -> list: ...
