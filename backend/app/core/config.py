"""
ApplyMate AI – Application Configuration
Reads from environment variables / .env file via Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────
    APP_NAME: str = "ApplyMate AI"
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "change-me-in-production-min-32-chars!"

    # ── Database ──────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/applymate_db"

    # ── CORS ──────────────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",")]
        return v

    # ── JWT ───────────────────────────────────────────────────────
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # ── Google Gemini ─────────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # ── Telegram ──────────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = ""

    # ── Email (Brevo) ─────────────────────────────────────────────
    BREVO_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@applymate.ai"
    EMAIL_FROM_NAME: str = "ApplyMate AI"

    # ── Admin ─────────────────────────────────────────────────────
    ADMIN_EMAIL: str = "admin@applymate.ai"
    ADMIN_PASSWORD: str = "admin123"

    # ── Scheduler ─────────────────────────────────────────────────
    SCRAPER_INTERVAL_MINUTES: int = 30

    # ── Rate Limiting ─────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance – call this everywhere."""
    return Settings()


settings = get_settings()
