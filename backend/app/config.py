"""Application configuration."""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_cors_origins() -> list[str]:
    """Local dev defaults plus any comma-separated origins in CORS_ORIGINS env."""
    base = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:3000",
    ]
    extra = os.environ.get("CORS_ORIGINS", "").strip()
    if extra:
        base.extend(o.strip() for o in extra.split(",") if o.strip())
    return base


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    API_TITLE: str = "QBI Visualizer API"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = "API for QBI Computation Visualization"

    CORS_ORIGINS: list[str] = _default_cors_origins()


settings = Settings()
