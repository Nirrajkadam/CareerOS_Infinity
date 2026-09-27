import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional
from uuid import UUID

# Configure basic application logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app.core.config")

class Settings(BaseSettings):
    """
    CareerOS Infinity Core Settings Configuration.
    Loads configurations from environment variables or .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = Field(default="CareerOS Infinity")
    VERSION: str = Field(default="1.0.0")
    API_V1_STR: str = Field(default="/api/v1")

    # DB Configurations
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:secure_postgres_password@db:5432/careeros_db"
    )

    # Redis Cache / Broker configs
    REDIS_URL: str = Field(
        default="redis://redis:6379/0"
    )

    # AI Configurations
    GEMINI_API_KEY: str = Field(default="")

    # Email Sync Configurations (Optional Real Inbox Connection)
    IMAP_USER_EMAIL: str = Field(default="")
    GMAIL_APP_PASSWORD: str = Field(default="")

    # Security Keys
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"])
    COOKIE_SECURE: bool = True
    ENABLE_SANDBOX_ATS: bool = False
    # Existing portal profiles and the credential vault are single-operator resources.
    DESKTOP_OPERATOR_USER_ID: Optional[UUID] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def use_async_postgres_driver(cls, value: str) -> str:
        # Hosting providers commonly return a PostgreSQL URL without a driver.
        for prefix in ("postgres://", "postgresql://"):
            if value.startswith(prefix):
                return "postgresql+asyncpg://" + value[len(prefix):]
        return value

    @field_validator("SECRET_KEY")
    @classmethod
    def reject_published_secret(cls, value: str) -> str:
        if value == "super_secret_jwt_sign_key_rotating_32_bytes_len":
            raise ValueError("Generate a private SECRET_KEY; the published development key is unsafe")
        return value

    @field_validator("CORS_ORIGINS")
    @classmethod
    def require_explicit_origins(cls, value: list[str]) -> list[str]:
        if "*" in value:
            raise ValueError("CORS_ORIGINS must contain explicit frontend origins")
        return value

# Instantiate single settings instance
settings = Settings()

import os
if settings.GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY

logger.info("Application settings loaded successfully.")
