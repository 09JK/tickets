"""
Question and QuestionAnswer models for ticket forms.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class Question(Base):
    """Question model for ticket category questions."""
    
    __tablename__ = "questions"
    
    # Primary key
    id = Column(String, primary_key=True)  # UUID
    
    # Category relationship
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    
    # Question details
    label = Column(String, nullable=False)
    placeholder = Column(String, nullable=True)
    value = Column(String, nullable=True)  # Default value
    
    # Validation
    type = Column(String, default="TEXT", nullable=False)  # TEXT, SELECT, etc.
    style = Column(Integer, default=2, nullable=False)  # 1=Short, 2=Paragraph
    required = Column(Boolean, default=True, nullable=False)
    min_length = Column(Integer, default=0, nullable=True)
    max_length = Column(Integer, default=4000, nullable=True)
    
    # Options for select questions
    options = Column(JSON, default=lambda: [], nullable=False)
    
    # Order
    order = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="questions")
    answers = relationship("QuestionAnswer", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id='{self.id}', label='{self.label}')>"


class QuestionAnswer(Base):
    """Answer to a question for a specific ticket."""
    
    __tablename__ = "questionAnswers"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relationships
    ticket_id = Column(String, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Answer
    value = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="question_answers")
    question = relationship("Question", back_populates="answers")
    user = relationship("User", back_populates="question_answers")
    
    def __repr__(self):
        return f"<QuestionAnswer(id={self.id}, ticket_id='{self.ticket_id}')>"