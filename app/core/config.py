"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration via environment variables."""

    # Database
    DATABASE_URL: str = "mysql+aiomysql://root:root@localhost:3306/agroflightops"

    # JWT
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # AWS S3
    S3_BUCKET: str = "agroflightops-docs-dev"
    S3_REGION: str = "us-east-1"
    S3_PRESIGNED_URL_EXPIRATION: int = 3600

    # CORS
    CORS_ORIGINS: str = "*"

    # App
    APP_ENV: str = "dev"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
