"""
Logging utilities for the Discord Tickets Bot.
"""

import logging
import sys
from typing import Optional
from pathlib import Path


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = "[{asctime}] [{levelname:8}] {name}: {message}"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure logging level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Setup logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        style="{",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logs_dir / "bot.log", encoding="utf-8")
        ]
    )
    
    # Reduce noise from discord.py
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    
    # Reduce noise from SQLAlchemy
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name or __name__)