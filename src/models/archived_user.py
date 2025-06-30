"""
Archived user model for ticket transcripts.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class ArchivedUser(Base):
    """Archived user for ticket transcripts."""
    
    __tablename__ = "archivedUsers"
    
    # Composite primary key
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String, primary_key=True)
    
    # User details at time of archiving
    username = Column(String, nullable=True)
    discriminator = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    bot = Column(Boolean, default=False, nullable=False)
    
    # Role assignment
    role_id = Column(String, nullable=True)  # References ArchivedRole
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="archived_users")
    role = relationship(
        "ArchivedRole", 
        foreign_keys=[ticket_id, role_id],
        back_populates="archived_users"
    )
    archived_messages = relationship(
        "ArchivedMessage",
        foreign_keys="ArchivedMessage.author_id",
        back_populates="author"
    )
    
    def __repr__(self):
        return f"<ArchivedUser(ticket_id='{self.ticket_id}', user_id='{self.user_id}')>"