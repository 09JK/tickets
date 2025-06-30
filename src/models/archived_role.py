"""
Archived role model for ticket transcripts.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class ArchivedRole(Base):
    """Archived role for ticket transcripts."""
    
    __tablename__ = "archivedRoles"
    
    # Composite primary key
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(String, primary_key=True)
    
    # Role details at time of archiving
    name = Column(String, nullable=False)
    colour = Column(String, default="5865F2", nullable=False)  # Discord blue
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="archived_roles")
    archived_users = relationship(
        "ArchivedUser",
        foreign_keys="ArchivedUser.role_id",
        back_populates="role"
    )
    
    def __repr__(self):
        return f"<ArchivedRole(ticket_id='{self.ticket_id}', role_id='{self.role_id}', name='{self.name}')>"