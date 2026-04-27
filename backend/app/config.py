"""Application configuration."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GitHub Configuration
    GITHUB_REPO: str = "https://github.com/PolicyEngine/policyengine-us.git"
    GITHUB_BRANCH: str = "master"
    AUTO_SYNC_MINUTES: int = 30

    # Local Paths
    REPOS_DIR: Path = Path("./data/repos")
    CACHE_DIR: Path = Path("./data/cache")

    # TAXSIM Integration (Optional)
    TAXSIM_PATH: Optional[Path] = None
    TAXSIM_EXECUTABLE: str = "taxsim35"

    # API Configuration
    API_TITLE: str = "QBI Visualizer API"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = "API for QBI Computation Visualization"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:3000",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
