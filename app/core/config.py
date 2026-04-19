"""
Application configuration using Pydantic Settings.

All configuration values are loaded from environment variables or
the .env file. This means:
  - Locally: values come from the .env file
  - On GCP: values come from cloud environment variables or Secret Manager

Why Pydantic Settings? Because it validates config values the same way
Pydantic validates API data. If DATABASE_URL is missing, the app refuses
to start with a clear error — not a cryptic crash later.

Never hardcode secrets (passwords, keys) in code. Always use env vars.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Student Sentiment Analysis API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/sentiment_db"

    # API
    api_v1_prefix: str = "/api/v1"

    # Performance
    workers: int = 4
    max_connections: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()