"""
Archive models for ticket transcripts and data preservation.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class ArchivedMessage(Base):
    """Archived message for ticket transcripts."""
    
    __tablename__ = "archivedMessages"
    
    # Primary key
    id = Column(String, primary_key=True)  # Discord message ID
    
    # Ticket relationship
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(String, nullable=False)  # References ArchivedUser
    
    # Message content
    content = Column(Text, nullable=False)
    
    # Message state
    deleted = Column(Boolean, default=False, nullable=False)
    edited = Column(Boolean, default=False, nullable=False)
    external = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="archived_messages")
    author = relationship(
        "ArchivedUser", 
        foreign_keys=[ticket_id, author_id],
        back_populates="archived_messages"
    )
    
    def __repr__(self):
        return f"<ArchivedMessage(id='{self.id}', ticket_id='{self.ticket_id}')>"