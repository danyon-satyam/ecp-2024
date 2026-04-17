"""
SQLAlchemy database model for student feedback.

A model defines the structure of a database table using Python classes.
SQLAlchemy maps this class to a real table called 'student_feedback'
in PostgreSQL.

Why use a model instead of raw SQL?
  - Type safety: Python knows the column types
  - No SQL injection risk: SQLAlchemy handles escaping
  - Database agnostic: swap PostgreSQL for another DB by changing one config line
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Every model inherits from this. SQLAlchemy uses it to track
    all tables and generate CREATE TABLE statements.
    """
    pass


class StudentFeedback(Base):
    """
    Database model for student feedback records.

    Maps to the 'student_feedback' table in PostgreSQL.
    Each instance of this class = one row in the table.
    """

    __tablename__ = "student_feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    roll_number = Column(String(20), nullable=False, index=True)
    gender = Column(String(10), nullable=False)
    age = Column(Integer, nullable=False)
    study_hours_per_day = Column(Integer, nullable=False)
    attendance_percentage = Column(Integer, nullable=False)
    active_backlogs = Column(Integer, nullable=False, default=0)
    academic_feedback = Column(String(20), nullable=False)
    emotional_feedback = Column(String(20), nullable=False)
    sentiment_label = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<StudentFeedback id={self.id} "
            f"roll={self.roll_number} "
            f"sentiment={self.sentiment_label}>"
        )