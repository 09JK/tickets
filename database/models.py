"""Database models converted from Prisma schema."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text,
    UniqueConstraint, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

Base = declarative_base()


class Guild(Base):
    """Guild configuration model."""
    __tablename__ = "guilds"
    
    id = Column(String, primary_key=True)
    auto_close = Column(Integer, default=43200000)  # 12 hours in ms
    auto_tag = Column(String, default="[]")
    archive = Column(Boolean, default=True)
    blocklist = Column(String, default="[]")
    claim_button = Column(Boolean, default=False)
    close_button = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    error_colour = Column(String, default="Red")
    footer = Column(String, default="Discord Tickets by eartharoid")
    locale = Column(String, default="en-GB")
    log_channel = Column(String, nullable=True)
    primary_colour = Column(String, default="#009999")
    stale_after = Column(Integer, nullable=True)
    success_colour = Column(String, default="Green")
    working_hours = Column(String, default='["UTC", ["00:00","23:59"], ["00:00","23:59"], ["00:00","23:59"], ["00:00","23:59"], ["00:00","23:59"], ["00:00","23:59"], ["00:00","23:59"]]')
    
    # Relationships
    categories = relationship("Category", back_populates="guild", cascade="all, delete")
    tickets = relationship("Ticket", back_populates="guild", cascade="all, delete")
    feedback = relationship("Feedback", back_populates="guild", cascade="all, delete")
    tags = relationship("Tag", back_populates="guild", cascade="all, delete")


class Category(Base):
    """Ticket category model."""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_name = Column(String, nullable=False)
    claiming = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    cooldown = Column(Integer, nullable=True)
    custom_topic = Column(String, nullable=True)
    description = Column(String, nullable=False)
    discord_category = Column(String, nullable=False)
    emoji = Column(String, nullable=False)
    enable_feedback = Column(Boolean, default=False)
    guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    image = Column(String, nullable=True)
    member_limit = Column(Integer, default=1)
    name = Column(String, nullable=False)
    opening_message = Column(String, nullable=False)
    ping_roles = Column(String, default="[]")
    ratelimit = Column(Integer, nullable=True)
    required_roles = Column(String, default="[]")
    require_topic = Column(Boolean, default=False)
    staff_roles = Column(String, nullable=False)
    total_limit = Column(Integer, default=50)
    
    # Relationships
    guild = relationship("Guild", back_populates="categories")
    tickets = relationship("Ticket", back_populates="category", cascade="all, delete")
    questions = relationship("Question", back_populates="category", cascade="all, delete")


class Ticket(Base):
    """Ticket model."""
    __tablename__ = "tickets"
    
    id = Column(String, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    claimed_by_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    closed_at = Column(DateTime, nullable=True)
    closed_by_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    closed_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    created_by_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    first_response_at = Column(DateTime, nullable=True)
    guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    last_message_at = Column(DateTime, default=func.now())
    number = Column(Integer, nullable=False)
    open = Column(Boolean, default=True)
    opening_message_id = Column(String, nullable=True)
    pinned_message_ids = Column(String, default="[]")
    priority = Column(String, default="MEDIUM")
    topic = Column(Text, nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="tickets")
    guild = relationship("Guild", back_populates="tickets")
    created_by = relationship("User", foreign_keys=[created_by_id])
    claimed_by = relationship("User", foreign_keys=[claimed_by_id])
    closed_by = relationship("User", foreign_keys=[closed_by_id])
    question_answers = relationship("QuestionAnswer", back_populates="ticket", cascade="all, delete")
    archived_channels = relationship("ArchivedChannel", back_populates="ticket", cascade="all, delete")
    archived_messages = relationship("ArchivedMessage", back_populates="ticket", cascade="all, delete")
    archived_users = relationship("ArchivedUser", back_populates="ticket", cascade="all, delete")
    archived_roles = relationship("ArchivedRole", back_populates="ticket", cascade="all, delete")
    feedback = relationship("Feedback", back_populates="ticket", cascade="all, delete")


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    message_count = Column(Integer, default=0)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="user")


class Question(Base):
    """Question model for ticket categories."""
    __tablename__ = "questions"
    
    id = Column(String, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    label = Column(String, nullable=False)
    max_length = Column(Integer, default=4000)
    min_length = Column(Integer, default=0)
    options = Column(String, default="[]")
    order = Column(Integer, nullable=False)
    placeholder = Column(String, nullable=True)
    required = Column(Boolean, default=True)
    style = Column(String, default="PARAGRAPH")
    type = Column(String, default="TEXT")
    
    # Relationships
    category = relationship("Category", back_populates="questions")
    answers = relationship("QuestionAnswer", back_populates="question", cascade="all, delete")


class QuestionAnswer(Base):
    """Question answer model."""
    __tablename__ = "question_answers"
    
    id = Column(String, primary_key=True)
    question_id = Column(String, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    value = Column(Text, nullable=True)
    
    # Relationships
    question = relationship("Question", back_populates="answers")
    ticket = relationship("Ticket", back_populates="question_answers")


class Tag(Base):
    """Tag model."""
    __tablename__ = "tags"
    
    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    regex = Column(Boolean, default=False)
    
    # Relationships
    guild = relationship("Guild", back_populates="tags")


class Feedback(Base):
    """Feedback model."""
    __tablename__ = "feedback"
    
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    # Relationships
    guild = relationship("Guild", back_populates="feedback")
    ticket = relationship("Ticket", back_populates="feedback")
    user = relationship("User", back_populates="feedback")


# Archive models
class ArchivedChannel(Base):
    """Archived channel model."""
    __tablename__ = "archived_channels"
    
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    channel_id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    name = Column(String, nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="archived_channels")
    
    __table_args__ = (
        UniqueConstraint('ticket_id', 'channel_id'),
    )


class ArchivedMessage(Base):
    """Archived message model."""
    __tablename__ = "archived_messages"
    
    id = Column(String, primary_key=True)
    author_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    deleted = Column(Boolean, default=False)
    edited = Column(Boolean, default=False)
    external = Column(Boolean, default=False)
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="archived_messages")


class ArchivedUser(Base):
    """Archived user model."""
    __tablename__ = "archived_users"
    
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String, primary_key=True)
    avatar = Column(String, nullable=True)
    bot = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    discriminator = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    role_id = Column(String, nullable=True)
    username = Column(String, nullable=True)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="archived_users")
    
    __table_args__ = (
        UniqueConstraint('ticket_id', 'user_id'),
    )


class ArchivedRole(Base):
    """Archived role model."""
    __tablename__ = "archived_roles"
    
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(String, primary_key=True)
    colour = Column(String, default="5865F2")
    created_at = Column(DateTime, default=func.now())
    name = Column(String, nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="archived_roles")
    
    __table_args__ = (
        UniqueConstraint('ticket_id', 'role_id'),
    )


# Database initialization
async def init_db(database_url: str):
    """Initialize database connection and create tables."""
    engine = create_async_engine(database_url, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    return engine, async_session_factory