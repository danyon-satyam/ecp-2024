"""
Feedback Repository — database access layer.

The Repository Pattern creates a clean separation between:
  - Business logic (sentiment calculation) in services/sentiment.py
  - Database operations (CRUD) in this file
  - API routing (HTTP handling) in api/v1/endpoints/feedback.py

Why this matters:
  If you want to switch from PostgreSQL to MongoDB tomorrow,
  you only rewrite this file. Nothing else changes — not the
  endpoints, not the schemas, not the tests. This is exactly
  the kind of enterprise architecture Pramit expects.

Each method has one job. No method does two database operations.
This makes testing and debugging straightforward.
"""
from sqlalchemy.orm import Session

from app.models.feedback import StudentFeedback
from app.schemas.student import StudentFeedbackCreate, StudentFeedbackUpdate
from app.services.sentiment import calculate_sentiment


class FeedbackRepository:
    """
    Repository for all student feedback database operations.

    Accepts a SQLAlchemy Session in the constructor.
    This makes it easy to inject a test session during testing.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialise the repository with a database session.

        Args:
            db: SQLAlchemy session provided by FastAPI's Depends(get_db)
        """
        self.db = db

    def create(self, feedback: StudentFeedbackCreate) -> StudentFeedback:
        """
        Create a new student feedback record in the database.

        Calculates sentiment automatically before saving.

        Args:
            feedback: Validated feedback data from the API request

        Returns:
            The newly created StudentFeedback database record
        """
        sentiment_label = calculate_sentiment(
            emotional_feedback=feedback.emotional_feedback,
            academic_feedback=feedback.academic_feedback,
        )

        db_record = StudentFeedback(
            **feedback.model_dump(),
            sentiment_label=sentiment_label,
        )

        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)  # Refresh to get the auto-generated ID
        return db_record

    def get_all(self, skip: int = 0, limit: int = 100) -> list[StudentFeedback]:
        """
        Retrieve all feedback records with pagination.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of StudentFeedback records
        """
        return (
            self.db.query(StudentFeedback)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, record_id: int) -> StudentFeedback | None:
        """
        Retrieve a single feedback record by its ID.

        Args:
            record_id: The primary key ID of the record

        Returns:
            StudentFeedback record if found, None otherwise
        """
        return (
            self.db.query(StudentFeedback)
            .filter(StudentFeedback.id == record_id)
            .first()
        )

    def update(
        self, record: StudentFeedback, updates: StudentFeedbackUpdate
    ) -> StudentFeedback:
        """
        Apply partial updates to an existing feedback record.

        Only updates fields that were actually sent in the request.
        Recalculates sentiment after any update.

        Args:
            record: The existing database record to update
            updates: Partial update data from the API request

        Returns:
            The updated StudentFeedback record
        """
        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)

        # Recalculate sentiment after update
        record.sentiment_label = calculate_sentiment(
            emotional_feedback=record.emotional_feedback,
            academic_feedback=record.academic_feedback,
        )

        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record: StudentFeedback) -> None:
        """
        Delete a feedback record from the database.

        Args:
            record: The database record to delete
        """
        self.db.delete(record)
        self.db.commit()

    def count_by_sentiment(self) -> dict:
        """
        Count records grouped by sentiment label.

        Used for the summary dashboard endpoint.
        Returns counts and percentages for Positive, Neutral, Negative.
        """
        total = self.db.query(StudentFeedback).count()
        if total == 0:
            return {
                "total": 0,
                "positive": 0, "positive_percentage": 0.0,
                "neutral": 0, "neutral_percentage": 0.0,
                "negative": 0, "negative_percentage": 0.0,
            }

        positive = (
            self.db.query(StudentFeedback)
            .filter(StudentFeedback.sentiment_label == "Positive")
            .count()
        )
        neutral = (
            self.db.query(StudentFeedback)
            .filter(StudentFeedback.sentiment_label == "Neutral")
            .count()
        )
        negative = (
            self.db.query(StudentFeedback)
            .filter(StudentFeedback.sentiment_label == "Negative")
            .count()
        )

        return {
            "total": total,
            "positive": positive,
            "positive_percentage": round((positive / total) * 100, 2),
            "neutral": neutral,
            "neutral_percentage": round((neutral / total) * 100, 2),
            "negative": negative,
            "negative_percentage": round((negative / total) * 100, 2),
        }