"""
Student Feedback API endpoints.

All endpoint functions are async def — this allows FastAPI to handle
hundreds of concurrent requests on a single event loop without blocking.

FastAPI automatically runs Depends(get_db) in a thread pool when used
inside async functions, so synchronous SQLAlchemy works safely here.
"""
from fastapi import APIRouter, Depends, status
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
    """Dependency that creates a FeedbackRepository for each request."""
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
async def submit_feedback(
    feedback: StudentFeedbackCreate,
    repo: FeedbackRepository = Depends(_get_repo),
) -> StudentFeedbackResponse:
    """
    Submit new student feedback.

    async def allows FastAPI to handle concurrent submissions without
    blocking — critical when 100s of students submit simultaneously.
    """
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
async def get_all_feedback(
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
            StudentFeedbackResponse(
                **r.__dict__,
                message="",
            ).model_dump()
            for r in records
        ],
    }


@router.get(
    "/feedback/{record_id}",
    response_model=StudentFeedbackResponse,
    summary="Get a single feedback record",
    tags=["Feedback"],
)
async def get_feedback_by_id(
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
async def update_feedback(
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
async def delete_feedback(
    record_id: int,
    repo: FeedbackRepository = Depends(_get_repo),
) -> None:
    """Delete a student feedback record permanently. Returns 204 on success."""
    record = _get_record_or_404(record_id, repo)
    repo.delete(record)