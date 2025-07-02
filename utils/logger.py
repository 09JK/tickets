"""Advanced logging setup with structured logging and rich console output."""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from rich.console import Console
from rich.logging import RichHandler


def setup_logger(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    json_logs: bool = False
) -> structlog.stdlib.BoundLogger:
    """
    Setup structured logging with rich console output.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        json_logs: Whether to use JSON formatting for file logs
        
    Returns:
        Configured logger instance
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=Console(stderr=True),
                rich_tracebacks=True,
                tracebacks_show_locals=True,
            )
        ],
        level=getattr(logging, level.upper()),
    )
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        if json_logs:
            file_handler.setFormatter(
                logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
            )
        else:
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
        logging.getLogger().addHandler(file_handler)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Get the logger
    logger = structlog.get_logger("discord-tickets")
    
    return logger


class BotLogger:
    """Specialized logger for different bot components."""
    
    def __init__(self, base_logger: structlog.stdlib.BoundLogger):
        self.base = base_logger
        
        # Component loggers
        self.commands = base_logger.bind(component="commands")
        self.buttons = base_logger.bind(component="buttons") 
        self.menus = base_logger.bind(component="menus")
        self.modals = base_logger.bind(component="modals")
        self.tickets = base_logger.bind(component="tickets")
        self.database = base_logger.bind(component="database")
        self.api = base_logger.bind(component="api")
        self.events = base_logger.bind(component="events")
    
    def info(self, component: str) -> structlog.stdlib.BoundLogger:
        """Get info logger for a component."""
        return getattr(self, component, self.base)
    
    def error(self, component: str) -> structlog.stdlib.BoundLogger:
        """Get error logger for a component.""" 
        return getattr(self, component, self.base)


def get_bot_logger() -> BotLogger:
    """Get the bot logger instance."""
    base_logger = structlog.get_logger("discord-tickets")
    return BotLogger(base_logger)