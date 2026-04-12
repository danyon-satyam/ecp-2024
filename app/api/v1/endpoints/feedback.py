"""
Student Feedback endpoints.

This module defines all API routes related to student feedback submission.
Each function here is one API endpoint that clients (web apps, mobile apps)
can call over the internet.
"""
from fastapi import APIRouter

from app.schemas.student import StudentFeedbackCreate, StudentFeedbackResponse

router = APIRouter()

# Temporary in-memory storage (we will replace with a real database on Day 7)
feedback_store: list[dict] = []


@router.post(
    "/feedback",
    response_model=StudentFeedbackResponse,
    summary="Submit student feedback",
    description="Submit a new student feedback record. The API will analyse the sentiment automatically.",
    tags=["Feedback"],
)
def submit_feedback(feedback: StudentFeedbackCreate) -> StudentFeedbackResponse:
    """
    Submit student feedback for sentiment analysis.

    - **roll_number**: Unique student identifier
    - **academic_feedback**: Student's satisfaction with academics
    - **emotional_feedback**: Student's emotional state
    - Returns a sentiment label: Positive, Neutral, or Negative
    """
    # Simple sentiment logic (we will replace with our ML model on Days 9-10)
    positive = {"Happy", "Glad", "Excellent", "Good"}
    negative = {"Sad", "Angry", "Bad"}

    score = 0
    if feedback.emotional_feedback in positive:
        score += 1
    elif feedback.emotional_feedback in negative:
        score -= 1

    if feedback.academic_feedback in positive:
        score += 1
    elif feedback.academic_feedback in negative:
        score -= 1

    if score > 0:
        sentiment = "Positive"
    elif score < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    # Store in memory temporarily
    record_id = len(feedback_store) + 1
    record = {
        "id": record_id,
        **feedback.model_dump(),
        "sentiment_label": sentiment,
    }
    feedback_store.append(record)

    return StudentFeedbackResponse(
        id=record_id,
        roll_number=feedback.roll_number,
        academic_feedback=feedback.academic_feedback,
        emotional_feedback=feedback.emotional_feedback,
        sentiment_label=sentiment,
        message=f"Feedback submitted successfully. Sentiment detected: {sentiment}",
    )


@router.get(
    "/feedback",
    summary="Get all feedback",
    description="Retrieve all submitted student feedback records.",
    tags=["Feedback"],
)
def get_all_feedback() -> list[dict]:
    """Return all stored feedback records."""
    return feedback_store