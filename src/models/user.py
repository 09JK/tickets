"""
User model for Discord users.
"""

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class User(Base):
    """User model for Discord users."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(String, primary_key=True)
    
    # Statistics
    message_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    tickets_created = relationship(
        "Ticket", 
        foreign_keys="Ticket.created_by_id",
        back_populates="created_by"
    )
    tickets_closed = relationship(
        "Ticket", 
        foreign_keys="Ticket.closed_by_id", 
        back_populates="closed_by"
    )
    tickets_claimed = relationship(
        "Ticket", 
        foreign_keys="Ticket.claimed_by_id",
        back_populates="claimed_by"
    )
    question_answers = relationship("QuestionAnswer", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")
    
    def __repr__(self):
        return f"<User(id='{self.id}', message_count={self.message_count})>"