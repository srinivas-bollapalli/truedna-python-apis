from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.audit_repository import AuditRepository
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService


async def get_user_repo(db: AsyncIOMotorDatabase = Depends(get_db)):
    return UserRepository(db)


async def get_token_repo(db: AsyncIOMotorDatabase = Depends(get_db)):
    return TokenRepository(db)


async def get_audit_service(db: AsyncIOMotorDatabase = Depends(get_db)):
    return AuditService(AuditRepository(db))


async def get_auth_service(
    user_repo=Depends(get_user_repo),
    token_repo=Depends(get_token_repo),
    audit_service=Depends(get_audit_service),
) -> AuthService:
    return AuthService(user_repo, token_repo, audit_service)
