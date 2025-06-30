"""
Archived channel model for ticket transcripts.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class ArchivedChannel(Base):
    """Archived channel for ticket transcripts."""
    
    __tablename__ = "archivedChannels"
    
    # Composite primary key
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    channel_id = Column(String, primary_key=True)
    
    # Channel details at time of archiving
    name = Column(String, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="archived_channels")
    
    def __repr__(self):
        return f"<ArchivedChannel(ticket_id='{self.ticket_id}', channel_id='{self.channel_id}', name='{self.name}')>"