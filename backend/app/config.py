"""Application configuration using Pydantic Settings."""
from typing import List
from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Adminory"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Database
    DATABASE_URL: PostgresDsn

    # Redis
    REDIS_URL: RedisDsn

    # JWT
    JWT_SECRET: str
    JWT_REFRESH_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Encryption (must be exactly 32 characters)
    ENCRYPTION_KEY: str

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in v.split(",")]

    # Email (optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@adminory.dev"
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "/tmp/uploads"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # SSO
    SSO_ENABLED: bool = True
    SSO_BASE_URL: str = "http://localhost:8000"

    # MCP
    MCP_ENABLED: bool = True
    MCP_INTERNAL_ENABLED: bool = True
    MCP_EXTERNAL_ENABLED: bool = True

    # Plugins
    PLUGINS_DIR: str = "./plugins"
    PLUGINS_ENABLED: bool = True
    PLUGIN_AUTO_RELOAD: bool = True

    # Celery
    CELERY_BROKER_URL: RedisDsn
    CELERY_RESULT_BACKEND: RedisDsn

    # Security
    SECRET_KEY: str
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    @field_validator("ALLOWED_HOSTS")
    @classmethod
    def parse_allowed_hosts(cls, v: str) -> List[str]:
        """Parse allowed hosts from comma-separated string."""
        return [host.strip() for host in v.split(",")]

    # Feature Flags
    FEATURE_SSO_SAML: bool = True
    FEATURE_SSO_OAUTH: bool = True
    FEATURE_PLUGINS: bool = True
    FEATURE_MCP: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Global settings instance
settings = Settings()
