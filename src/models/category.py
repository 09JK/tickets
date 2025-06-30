"""
Category model for ticket categories.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class Category(Base):
    """Category model for organizing tickets."""
    
    __tablename__ = "categories"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Guild relationship
    guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    
    # Basic info
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    emoji = Column(String, nullable=False)
    
    # Discord configuration
    discord_category = Column(String, nullable=False)  # Discord category channel ID
    channel_name = Column(String, nullable=False)
    
    # Messages
    opening_message = Column(Text, nullable=False)
    custom_topic = Column(String, nullable=True)
    
    # Requirements
    required_roles = Column(JSON, default=lambda: [], nullable=False)
    require_topic = Column(Boolean, default=False, nullable=False)
    
    # Staff configuration
    staff_roles = Column(JSON, nullable=False)  # List of role IDs
    ping_roles = Column(JSON, default=lambda: [], nullable=False)
    
    # Limits and cooldowns
    member_limit = Column(Integer, default=1, nullable=False)
    total_limit = Column(Integer, default=50, nullable=False)
    cooldown = Column(Integer, nullable=True)
    ratelimit = Column(Integer, nullable=True)
    
    # Features
    claiming = Column(Boolean, default=False, nullable=False)
    enable_feedback = Column(Boolean, default=False, nullable=False)
    
    # Image
    image = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    guild = relationship("Guild", back_populates="categories")
    tickets = relationship("Ticket", back_populates="category")
    questions = relationship("Question", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', guild_id='{self.guild_id}')>"