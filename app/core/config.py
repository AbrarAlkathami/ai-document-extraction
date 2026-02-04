from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the directory where this config file lives
_BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Central application configuration.

    Loads environment variables from `.env.local`, `.env.production`
    and `.env.example`.

    This class defines all runtime settings used across the application,
    including database connection, storage paths, and extraction behavior.
    """

    model_config = SettingsConfigDict(
        env_file=(
            _BASE_DIR / ".env.example",
            _BASE_DIR / ".env.local",
            _BASE_DIR / ".env.production",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App metadata
    APP_NAME: str
    APP_DESCRIPTION: str

    ENV: str
    LOG_LEVEL: str

    # Database
    DATABASE_URL: str

    # Storage
    STORAGE_DIR: str

    # Mock AI behavior
    MOCK_AI_DELAY_MS: int
    RECORDS_PER_DOCUMENT: int


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance"""
    return Settings()
