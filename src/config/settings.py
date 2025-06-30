"""
Bot configuration using Pydantic settings.
"""

from typing import List, Optional
from pydantic import BaseSettings, Field
from pydantic_settings import BaseSettings as PydanticBaseSettings


class Settings(PydanticBaseSettings):
    """Bot configuration settings."""
    
    # Bot settings
    bot_token: str = Field(..., env="BOT_TOKEN")
    version: str = "4.0.41-python"
    
    # Database settings
    database_url: str = Field("sqlite:///./user/database.db", env="DATABASE_URL")
    database_provider: str = Field("sqlite", env="DB_PROVIDER")
    
    # Logging settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Web server settings
    http_host: str = Field("0.0.0.0", env="HTTP_HOST")
    http_port: int = Field(8080, env="HTTP_PORT")
    http_external: str = Field("http://localhost:8080", env="HTTP_EXTERNAL")
    
    # Bot configuration
    primary_colour: str = "#009999"
    error_colour: str = "Red"
    success_colour: str = "Green"
    footer_text: str = "Discord Tickets by eartharoid"
    
    # Super users (bot operators)
    super_users: List[str] = Field(default_factory=list, env="SUPER_USERS")
    
    # Guild settings
    auto_close: int = 43200000  # 12 hours in milliseconds
    stale_after: Optional[int] = None
    archive: bool = True
    
    # Working hours (UTC timezone, 24h format)
    working_hours: List[str] = Field(
        default=[
            "UTC",
            ["00:00", "23:59"],  # Monday
            ["00:00", "23:59"],  # Tuesday
            ["00:00", "23:59"],  # Wednesday
            ["00:00", "23:59"],  # Thursday
            ["00:00", "23:59"],  # Friday
            ["00:00", "23:59"],  # Saturday
            ["00:00", "23:59"],  # Sunday
        ]
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"