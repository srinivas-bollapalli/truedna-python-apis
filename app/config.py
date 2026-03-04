from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "TrueDNA Python REST API"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # MongoDB
    mongo_uri: str
    mongo_db_name: str

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7


@lru_cache()
def get_settings() -> Settings:
    return Settings()
