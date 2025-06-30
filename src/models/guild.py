"""
Guild model for Discord server configuration.
"""

from typing import List, Optional
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class Guild(Base):
    """Guild (Discord server) configuration model."""
    
    __tablename__ = "guilds"
    
    # Primary key
    id = Column(String, primary_key=True)
    
    # Configuration
    locale = Column(String, default="en-GB", nullable=False)
    primary_colour = Column(String, default="#009999", nullable=False)
    error_colour = Column(String, default="Red", nullable=False)
    success_colour = Column(String, default="Green", nullable=False)
    footer = Column(String, default="Discord Tickets by eartharoid")
    
    # Auto-close and archiving
    auto_close = Column(Integer, default=43200000, nullable=False)  # 12 hours in ms
    stale_after = Column(Integer, nullable=True)
    archive = Column(Boolean, default=True, nullable=False)
    
    # Buttons
    claim_button = Column(Boolean, default=False, nullable=False)
    close_button = Column(Boolean, default=False, nullable=False)
    
    # Moderation
    blocklist = Column(JSON, default=lambda: [], nullable=False)
    auto_tag = Column(JSON, default=lambda: [], nullable=False)
    
    # Logging
    log_channel = Column(String, nullable=True)
    
    # Working hours - JSON array with timezone and time ranges
    working_hours = Column(
        JSON, 
        default=lambda: [
            "UTC",
            ["00:00", "23:59"],  # Monday
            ["00:00", "23:59"],  # Tuesday  
            ["00:00", "23:59"],  # Wednesday
            ["00:00", "23:59"],  # Thursday
            ["00:00", "23:59"],  # Friday
            ["00:00", "23:59"],  # Saturday
            ["00:00", "23:59"],  # Sunday
        ],
        nullable=False
    )
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    categories = relationship("Category", back_populates="guild", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="guild", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="guild", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="guild", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Guild(id='{self.id}', locale='{self.locale}')>"