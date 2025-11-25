from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # App
    app_name: str = "VisoMaster Admin API"
    environment: str = Field(default="local")
    debug: bool = Field(default=True)

    # Database
    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@db:5432/visomaster")

    # JWT / Auth
    jwt_secret: str = Field(default="change-me")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expires_minutes: int = Field(default=60 * 12)

    # S3 / MinIO
    s3_endpoint_url: Optional[str] = None
    s3_region: str = Field(default="us-east-1")
    s3_access_key: str = Field(default="minioadmin")
    s3_secret_key: str = Field(default="minioadmin")
    s3_bucket: str = Field(default="visomaster")
    s3_use_ssl: bool = Field(default=False)
    s3_presign_expire: int = Field(default=3600)

    # Seed admin
    seed_admin_username: Optional[str] = Field(default="admin")
    seed_admin_password: Optional[str] = Field(default="admin123")
    seed_admin_is_superadmin: bool = Field(default=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
