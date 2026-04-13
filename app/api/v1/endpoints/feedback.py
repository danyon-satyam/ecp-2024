"""
Student Feedback endpoints.

This module defines all CRUD API routes for student feedback.

CRUD stands for:
  - Create  → POST   /feedback
  - Read    → GET    /feedback      (all records)
  - Read    → GET    /feedback/{id} (single record)
  - Update  → PATCH  /feedback/{id}
  - Delete  → DELETE /feedback/{id}

Each operation returns the correct HTTP status code so clients
know exactly what happened.
"""
from fastapi import APIRouter, HTTPException, status

from app.schemas.student import (
    StudentFeedbackCreate,
    StudentFeedbackResponse,
    StudentFeedbackUpdate,
)
from app.services.sentiment import calculate_sentiment, get_sentiment_summary

router = APIRouter()

# Temporary in-memory storage (replaced with real database on Day 7)
# This acts like a simple list-based database for now
feedback_store: list[dict] = []


def _find_record(record_id: int) -> dict:
    """
    Find a feedback record by ID.

    This is a private helper function (note the underscore prefix).
    Private helpers are not API endpoints — they are internal utilities
    used by multiple endpoints to avoid repeating the same logic.

    Args:
        record_id: The ID of the record to find

    Raises:
        HTTPException: 404 if the record is not found

    Returns:
        The matching record dictionary
    """
    for record in feedback_store:
        if record["id"] == record_id:
            return record
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Feedback record with ID {record_id} not found.",
    )


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────

@router.post(
    "/feedback",
    response_model=StudentFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit student feedback",
    description="Submit a new student feedback record. Sentiment is calculated automatically.",
    tags=["Feedback"],
)
def submit_feedback(feedback: StudentFeedbackCreate) -> StudentFeedbackResponse:
    """
    Submit new student feedback.

    The sentiment label (Positive / Neutral / Negative) is calculated
    automatically using our sentiment service based on the student's
    emotional and academic feedback values.
    """
    sentiment_label = calculate_sentiment(
        emotional_feedback=feedback.emotional_feedback,
        academic_feedback=feedback.academic_feedback,
    )

    record_id = len(feedback_store) + 1
    record = {
        "id": record_id,
        **feedback.model_dump(),
        "sentiment_label": sentiment_label,
    }
    feedback_store.append(record)

    return StudentFeedbackResponse(
        **record,
        message=f"Feedback submitted. Sentiment detected: {sentiment_label}",
    )


# ─────────────────────────────────────────────
# READ ALL
# ─────────────────────────────────────────────

@router.get(
    "/feedback",
    summary="Get all feedback records",
    description="Retrieve all submitted student feedback records with sentiment summary.",
    tags=["Feedback"],
)
def get_all_feedback() -> dict:
    """
    Return all feedback records along with a sentiment summary.

    The summary shows the distribution of Positive / Neutral / Negative
    sentiments across all submitted records — useful for university dashboards.
    """
    return {
        "summary": get_sentiment_summary(feedback_store),
        "records": feedback_store,
    }


# ─────────────────────────────────────────────
# READ ONE
# ─────────────────────────────────────────────

@router.get(
    "/feedback/{record_id}",
    response_model=StudentFeedbackResponse,
    summary="Get a single feedback record",
    description="Retrieve one specific student feedback record by its ID.",
    tags=["Feedback"],
)
def get_feedback_by_id(record_id: int) -> StudentFeedbackResponse:
    """
    Retrieve a single feedback record by its unique ID.

    Returns 404 if the record does not exist.
    """
    record = _find_record(record_id)
    return StudentFeedbackResponse(
        **record,
        message="Record retrieved successfully.",
    )


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────

@router.patch(
    "/feedback/{record_id}",
    response_model=StudentFeedbackResponse,
    summary="Update a feedback record",
    description="Partially update an existing feedback record. Only send the fields you want to change.",
    tags=["Feedback"],
)
def update_feedback(record_id: int, updates: StudentFeedbackUpdate) -> StudentFeedbackResponse:
    """
    Partially update a student feedback record.

    Uses PATCH (not PUT) because we allow partial updates —
    the client only needs to send the fields they want to change.
    Sentiment is automatically recalculated after any update.
    """
    record = _find_record(record_id)

    # Apply only the fields that were actually sent (exclude_unset ignores fields not sent)
    update_data = updates.model_dump(exclude_unset=True)
    record.update(update_data)

    # Recalculate sentiment after update
    record["sentiment_label"] = calculate_sentiment(
        emotional_feedback=record["emotional_feedback"],
        academic_feedback=record["academic_feedback"],
    )

    return StudentFeedbackResponse(
        **record,
        message="Feedback record updated. Sentiment recalculated.",
    )


# ─────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────

@router.delete(
    "/feedback/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a feedback record",
    description="Permanently delete a student feedback record by its ID.",
    tags=["Feedback"],
)
def delete_feedback(record_id: int) -> None:
    """
    Delete a student feedback record permanently.

    Returns HTTP 204 No Content on success.
    204 means: the action was successful but there is nothing to return.
    This is the correct REST standard for DELETE operations.
    """
    record = _find_record(record_id)
    feedback_store.remove(record)