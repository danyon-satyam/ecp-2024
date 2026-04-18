"""
Analytics API endpoints.

These endpoints provide aggregated insights across all student feedback
records — the kind of data a university dashboard would display.

Unlike the feedback CRUD endpoints which operate on individual records,
analytics endpoints always return aggregated, anonymised statistics.

Endpoints:
  GET /analytics/summary        — overall sentiment distribution
  GET /analytics/by-sentiment   — filter records by sentiment label
  GET /analytics/trends         — sentiment breakdown by gender and feedback type
  GET /analytics/at-risk        — students flagged as potentially at risk
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.student_feedback import StudentFeedback
from app.services.feedback_repository import FeedbackRepository
from app.services.sentiment import get_model_info

router = APIRouter()


def _get_repo(db: Session = Depends(get_db)) -> FeedbackRepository:
    """Dependency that creates a FeedbackRepository for each request."""
    return FeedbackRepository(db)


@router.get(
    "/summary",
    summary="Overall sentiment summary",
    description="Returns total counts and percentages for each sentiment label.",
    tags=["Analytics"],
)
def get_summary(repo: FeedbackRepository = Depends(_get_repo)) -> dict:
    """
    Return the overall sentiment distribution across all records.

    This is the top-level dashboard number — what percentage of
    students are Positive, Neutral, or Negative overall.
    """
    summary = repo.count_by_sentiment()
    model_info = get_model_info()
    return {
        "sentiment_distribution": summary,
        "prediction_mode": model_info["mode"],
    }


@router.get(
    "/by-sentiment",
    summary="Filter records by sentiment",
    description="Retrieve all records with a specific sentiment label.",
    tags=["Analytics"],
)
def get_by_sentiment(
    sentiment: str = Query(
        ...,
        description="Sentiment label to filter by",
        pattern="^(Positive|Neutral|Negative)$",
    ),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Filter feedback records by sentiment label with pagination.

    Useful for a university to see specifically which students
    are Negative — those may need academic intervention.

    Args:
        sentiment: One of 'Positive', 'Neutral', 'Negative'
        skip: Pagination offset
        limit: Maximum records to return (capped at 200)
    """
    records = (
        db.query(StudentFeedback)
        .filter(StudentFeedback.sentiment_label == sentiment)
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = (
        db.query(StudentFeedback)
        .filter(StudentFeedback.sentiment_label == sentiment)
        .count()
    )

    return {
        "sentiment_filter": sentiment,
        "total_matching": total,
        "returned": len(records),
        "records": [
            {
                "id": r.id,
                "roll_number": r.roll_number,
                "gender": r.gender,
                "age": r.age,
                "attendance_percentage": r.attendance_percentage,
                "active_backlogs": r.active_backlogs,
                "academic_feedback": r.academic_feedback,
                "emotional_feedback": r.emotional_feedback,
                "sentiment_label": r.sentiment_label,
            }
            for r in records
        ],
    }


@router.get(
    "/trends",
    summary="Sentiment trends by demographics",
    description="Sentiment breakdown grouped by gender and feedback category.",
    tags=["Analytics"],
)
def get_trends(db: Session = Depends(get_db)) -> dict:
    """
    Return sentiment trends broken down by gender and feedback categories.

    This gives universities actionable insight — e.g. are male students
    more negative than female students? Are students with backlogs
    predominantly negative?
    """
    # Sentiment breakdown by gender
    gender_breakdown = (
        db.query(
            StudentFeedback.gender,
            StudentFeedback.sentiment_label,
            func.count(StudentFeedback.id).label("count"),
        )
        .group_by(StudentFeedback.gender, StudentFeedback.sentiment_label)
        .all()
    )

    # Sentiment breakdown by academic feedback
    academic_breakdown = (
        db.query(
            StudentFeedback.academic_feedback,
            StudentFeedback.sentiment_label,
            func.count(StudentFeedback.id).label("count"),
        )
        .group_by(
            StudentFeedback.academic_feedback,
            StudentFeedback.sentiment_label,
        )
        .all()
    )

    # Sentiment breakdown by emotional feedback
    emotional_breakdown = (
        db.query(
            StudentFeedback.emotional_feedback,
            StudentFeedback.sentiment_label,
            func.count(StudentFeedback.id).label("count"),
        )
        .group_by(
            StudentFeedback.emotional_feedback,
            StudentFeedback.sentiment_label,
        )
        .all()
    )

    return {
        "by_gender": [
            {"gender": r.gender, "sentiment": r.sentiment_label, "count": r.count}
            for r in gender_breakdown
        ],
        "by_academic_feedback": [
            {
                "academic_feedback": r.academic_feedback,
                "sentiment": r.sentiment_label,
                "count": r.count,
            }
            for r in academic_breakdown
        ],
        "by_emotional_feedback": [
            {
                "emotional_feedback": r.emotional_feedback,
                "sentiment": r.sentiment_label,
                "count": r.count,
            }
            for r in emotional_breakdown
        ],
    }


@router.get(
    "/at-risk",
    summary="At-risk students",
    description="Students flagged as potentially at risk based on negative sentiment, high backlogs, or low attendance.",
    tags=["Analytics"],
)
def get_at_risk_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> dict:
    """
    Identify students who may need academic intervention.

    A student is considered at-risk if they meet ANY of:
      - Negative sentiment label
      - 2 or more active backlogs
      - Attendance below 60%

    This endpoint powers the university's early-warning dashboard.
    Early identification allows counsellors to reach out proactively.
    """
    at_risk = (
        db.query(StudentFeedback)
        .filter(
            (StudentFeedback.sentiment_label == "Negative")
            | (StudentFeedback.active_backlogs >= 2)
            | (StudentFeedback.attendance_percentage < 60)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    total_at_risk = (
        db.query(StudentFeedback)
        .filter(
            (StudentFeedback.sentiment_label == "Negative")
            | (StudentFeedback.active_backlogs >= 2)
            | (StudentFeedback.attendance_percentage < 60)
        )
        .count()
    )

    total_students = db.query(StudentFeedback).count()

    return {
        "total_at_risk": total_at_risk,
        "at_risk_percentage": (
            round((total_at_risk / total_students) * 100, 2)
            if total_students > 0
            else 0.0
        ),
        "criteria": [
            "Negative sentiment label",
            "2 or more active backlogs",
            "Attendance below 60%",
        ],
        "records": [
            {
                "id": r.id,
                "roll_number": r.roll_number,
                "sentiment_label": r.sentiment_label,
                "active_backlogs": r.active_backlogs,
                "attendance_percentage": r.attendance_percentage,
                "emotional_feedback": r.emotional_feedback,
            }
            for r in at_risk
        ],
    }