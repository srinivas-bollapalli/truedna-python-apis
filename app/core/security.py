from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str) -> tuple[str, str]:
    """Returns (token, jti)."""
    jti = str(uuid4())
    payload = {
        "sub": user_id,
        "jti": jti,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        ),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti


def create_refresh_token(user_id: str) -> tuple[str, datetime]:
    """Returns (token, expires_at)."""
    expires = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": str(uuid4()),
        "exp": expires,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
