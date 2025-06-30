"""
Tag model for quick response tags.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class Tag(Base):
    """Tag model for quick response tags."""
    
    __tablename__ = "tags"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Guild relationship
    guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    
    # Tag details
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    regex = Column(String, nullable=True)  # Optional regex pattern
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    guild = relationship("Guild", back_populates="tags")
    
    # Unique constraint on guild_id + name is handled in the database schema
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', guild_id='{self.guild_id}')>"