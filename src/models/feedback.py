"""
Feedback model for ticket ratings and comments.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class Feedback(Base):
    """Feedback model for ticket ratings."""
    
    __tablename__ = "feedback"
    
    # Primary key (one feedback per ticket)
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    
    # Guild and user
    guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    # Feedback content
    rating = Column(Integer, nullable=False)  # 1-5 star rating
    comment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="feedback")
    guild = relationship("Guild", back_populates="feedback")
    user = relationship("User", back_populates="feedback")
    
    def __repr__(self):
        return f"<Feedback(ticket_id='{self.ticket_id}', rating={self.rating})>"