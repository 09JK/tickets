"""
Database configuration and setup using SQLAlchemy.
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""
    metadata = MetaData()


class Database:
    """Database connection and session management."""
    
    def __init__(self, database_url: str):
        """Initialize database with connection URL."""
        self.database_url = database_url
        
        # Convert sqlite URLs to async format
        if database_url.startswith("sqlite:"):
            self.database_url = database_url.replace("sqlite:", "sqlite+aiosqlite:")
        elif database_url.startswith("postgresql:"):
            self.database_url = database_url.replace("postgresql:", "postgresql+asyncpg:")
        
        self.engine = None
        self.async_session = None
    
    async def initialize(self):
        """Initialize database connection and create tables."""
        self.engine = create_async_engine(
            self.database_url,
            echo=False,  # Set to True for SQL debugging
            future=True
        )
        
        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Import all models to ensure they're registered
        from models import (
            ticket, category, guild, user, question, 
            feedback, tag, archived_message, archived_user, archived_role, archived_channel
        )
        
        # Create all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session."""
        if not self.async_session:
            raise RuntimeError("Database not initialized")
        
        async with self.async_session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")