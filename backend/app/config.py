from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    API_V1_PREFIX: str = "/api/v1"
    API_KEY: str = "dev-api-key-change-in-production"

    DATABASE_URL: str = "sqlite:///./carrier_sales.db"

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    FMCSA_API_URL: str = "https://mobile.fmcsa.dot.gov/qc/services/carriers"
    FMCSA_API_KEY: str = ""

    HAPPYROBOT_WEBHOOK_SECRET: str = ""  # For validating webhook calls

    ENVIRONMENT: str = "development"
    APP_DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_ignore_empty = True


settings = Settings()
