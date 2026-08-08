try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # Pydantic v1 compatibility

from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AutoPersona AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "autopersona-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./autopersona.db"
    )

    # AI API Config
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")

    # Autonomous Scheduler Settings
    SCHEDULER_INTERVAL_MINUTES: int = 15
    MIN_QUALITY_SCORE: float = 7.0

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
