"""Environment variable validation and loading."""

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Bot configuration settings."""
    
    # Database settings
    db_provider: str = "sqlite"
    db_connection_url: Optional[str] = None
    
    # Discord settings
    discord_token: str
    discord_secret: str
    
    # Security
    encryption_key: str
    
    # HTTP settings
    http_host: str = "0.0.0.0"
    http_port: int = 8080
    http_external: str
    http_internal: Optional[str] = None
    http_trust_proxy: bool = False
    
    # Optional settings
    public_bot: bool = False
    publish_commands: bool = True
    invalidate_tokens: Optional[str] = None
    override_archive: bool = False
    super_users: str = "[]"
    
    @validator("db_connection_url")
    def validate_db_url(cls, v, values):
        """Validate database connection URL."""
        db_provider = values.get("db_provider", "sqlite")
        if db_provider != "sqlite" and not v:
            raise ValueError("DB_CONNECTION_URL must be set when DB_PROVIDER is not 'sqlite'")
        return v
    
    @validator("db_provider")
    def validate_db_provider(cls, v):
        """Validate database provider."""
        allowed = ["mysql", "postgresql", "sqlite"]
        if v not in allowed:
            raise ValueError(f"DB_PROVIDER must be one of: {', '.join(allowed)}")
        return v
    
    @validator("encryption_key")
    def validate_encryption_key(cls, v):
        """Validate encryption key length."""
        if len(v) < 48:
            raise ValueError("ENCRYPTION_KEY must be at least 48 characters long")
        return v
    
    @validator("http_external")
    def validate_http_external(cls, v):
        """Validate external HTTP URL."""
        if not v.startswith("http"):
            raise ValueError("HTTP_EXTERNAL must be a valid URL")
        return v.rstrip("/")
    
    @validator("http_host")
    def validate_http_host(cls, v):
        """Validate HTTP host."""
        if v.startswith("http"):
            raise ValueError("HTTP_HOST must be an address, not a URL")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def load_environment() -> Settings:
    """Load and validate environment variables."""
    # Load .env file if it exists
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
    
    try:
        settings = Settings()
        return settings
    except Exception as e:
        print(f"❌ Environment validation error: {e}")
        sys.exit(1)


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global settings
    if settings is None:
        settings = load_environment()
    return settings