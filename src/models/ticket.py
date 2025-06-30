"""
Ticket model for support tickets.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class Ticket(Base):
    """Ticket model for support tickets."""
    
    __tablename__ = "tickets"
    
    # Primary key
    id = Column(String, primary_key=True)  # Discord channel ID
    
    # Guild and category
    guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)
    
    # Ticket info
    number = Column(Integer, nullable=False)  # Sequential number within guild
    topic = Column(Text, nullable=True)
    priority = Column(String, nullable=True)
    
    # Status
    open = Column(Boolean, default=True, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)
    
    # Users
    created_by_id = Column(String, ForeignKey("users.id"), nullable=False)
    claimed_by_id = Column(String, ForeignKey("users.id"), nullable=True)
    closed_by_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # References
    references_ticket_id = Column(String, ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True)
    references_message_id = Column(String, nullable=True)
    
    # Messages
    opening_message_id = Column(String, nullable=False)
    pinned_message_ids = Column(JSON, default=lambda: [], nullable=False)
    
    # Statistics
    message_count = Column(Integer, nullable=True)
    
    # Closure info
    closed_reason = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    closed_at = Column(DateTime, nullable=True)
    first_response_at = Column(DateTime, nullable=True)
    last_message_at = Column(DateTime, nullable=True)
    
    # Relationships
    guild = relationship("Guild", back_populates="tickets")
    category = relationship("Category", back_populates="tickets")
    
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="tickets_created")
    claimed_by = relationship("User", foreign_keys=[claimed_by_id], back_populates="tickets_claimed")
    closed_by = relationship("User", foreign_keys=[closed_by_id], back_populates="tickets_closed")
    
    references_ticket = relationship("Ticket", remote_side=[id], back_populates="referenced_by")
    referenced_by = relationship("Ticket", back_populates="references_ticket")
    
    question_answers = relationship("QuestionAnswer", back_populates="ticket", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    
    # Archive relationships
    archived_messages = relationship("ArchivedMessage", back_populates="ticket", cascade="all, delete-orphan")
    archived_users = relationship("ArchivedUser", back_populates="ticket", cascade="all, delete-orphan")
    archived_roles = relationship("ArchivedRole", back_populates="ticket", cascade="all, delete-orphan")
    archived_channels = relationship("ArchivedChannel", back_populates="ticket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket(id='{self.id}', number={self.number}, open={self.open})>"