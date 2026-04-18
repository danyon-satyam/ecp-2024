"""
Student Feedback API endpoints.

These endpoints now use the FeedbackRepository for all database operations.
Notice how clean these functions are — they handle HTTP concerns only:
  - Parse the request
  - Call the repository
  - Return the response with the correct status code

All database logic lives in FeedbackRepository.
All sentiment logic lives in sentiment.py.
This file only handles HTTP. One responsibility per file.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import RecordNotFoundException
from app.schemas.student import (
    StudentFeedbackCreate,
    StudentFeedbackResponse,
    StudentFeedbackUpdate,
)
from app.services.feedback_repository import FeedbackRepository

router = APIRouter()


def _get_repo(db: Session = Depends(get_db)) -> FeedbackRepository:
    """
    FastAPI dependency that creates a FeedbackRepository for each request.

    Depends(get_db) injects a database session automatically.
    This function wraps it in a repository and passes it to the endpoint.
    """
    return FeedbackRepository(db)


def _get_record_or_404(record_id: int, repo: FeedbackRepository):
    """
    Fetch a record by ID or raise RecordNotFoundException.

    Raises our domain exception instead of HTTPException directly.
    The global error handler converts it to the correct HTTP response.
    """
    record = repo.get_by_id(record_id)
    if not record:
        raise RecordNotFoundException(record_id)
    return record


@router.post(
    "/feedback",
    response_model=StudentFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit student feedback",
    tags=["Feedback"],
)
def submit_feedback(
    feedback: StudentFeedbackCreate,
    repo: FeedbackRepository = Depends(_get_repo),
) -> StudentFeedbackResponse:
    """Submit new student feedback. Sentiment is calculated automatically."""
    record = repo.create(feedback)
    return StudentFeedbackResponse(
        **record.__dict__,
        message=f"Feedback submitted. Sentiment: {record.sentiment_label}",
    )


@router.get(
    "/feedback",
    summary="Get all feedback records",
    tags=["Feedback"],
)
def get_all_feedback(
    skip: int = 0,
    limit: int = 100,
    repo: FeedbackRepository = Depends(_get_repo),
) -> dict:
    """Return all feedback records with sentiment summary and pagination."""
    records = repo.get_all(skip=skip, limit=limit)
    summary = repo.count_by_sentiment()
    return {
        "summary": summary,
        "records": [
            StudentFeedbackResponse(**r.__dict__, message="").model_dump()
            for r in records
        ],
    }


@router.get(
    "/feedback/{record_id}",
    response_model=StudentFeedbackResponse,
    summary="Get a single feedback record",
    tags=["Feedback"],
)
def get_feedback_by_id(
    record_id: int,
    repo: FeedbackRepository = Depends(_get_repo),
) -> StudentFeedbackResponse:
    """Retrieve one feedback record by ID. Returns 404 if not found."""
    record = _get_record_or_404(record_id, repo)
    return StudentFeedbackResponse(
        **record.__dict__,
        message="Record retrieved successfully.",
    )


@router.patch(
    "/feedback/{record_id}",
    response_model=StudentFeedbackResponse,
    summary="Update a feedback record",
    tags=["Feedback"],
)
def update_feedback(
    record_id: int,
    updates: StudentFeedbackUpdate,
    repo: FeedbackRepository = Depends(_get_repo),
) -> StudentFeedbackResponse:
    """Partially update a feedback record. Sentiment is recalculated automatically."""
    record = _get_record_or_404(record_id, repo)
    updated = repo.update(record, updates)
    return StudentFeedbackResponse(
        **updated.__dict__,
        message="Record updated. Sentiment recalculated.",
    )


@router.delete(
    "/feedback/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a feedback record",
    tags=["Feedback"],
)
def delete_feedback(
    record_id: int,
    repo: FeedbackRepository = Depends(_get_repo),
) -> None:
    """Delete a feedback record permanently. Returns 204 on success."""
    record = _get_record_or_404(record_id, repo)
    repo.delete(record)