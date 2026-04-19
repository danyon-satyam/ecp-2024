"""
Visualisation API endpoints.

These endpoints generate and return Seaborn chart images as PNG files
directly over HTTP. A university dashboard can call these endpoints
and embed the charts in their web interface without any post-processing.

Why return images from the API instead of raw data?
  For non-technical university staff, a ready-made chart is far more
  useful than JSON numbers they would need to plot themselves.
  This makes the API a complete analytics solution, not just a data store.

Technical approach:
  - Charts are generated in-memory using BytesIO (no disk writes)
  - StreamingResponse streams the PNG bytes directly to the client
  - Response headers set Content-Type to image/png so browsers
    display the image directly when the URL is opened
  - All charts use the same colour scheme: Green=Positive,
    Blue=Neutral, Red=Negative for visual consistency

How to use in a browser:
  Open http://127.0.0.1:8000/api/v1/visualisations/sentiment-bar
  The chart image displays directly in the browser tab.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.student_feedback import StudentFeedback
from app.services import visualisation as viz_service

router = APIRouter()


def _get_all_records_as_dicts(db: Session) -> list[dict]:
    """
    Fetch all feedback records and convert to list of dicts.

    Used by all visualisation endpoints as their data source.

    Args:
        db: Database session

    Returns:
        List of record dictionaries

    Raises:
        HTTPException: 404 if no records exist in the database
    """
    records = db.query(StudentFeedback).all()
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No feedback records found. "
                "Please seed the database first using: "
                "python scripts/seed_database.py"
            ),
        )
    return [
        {
            "id": r.id,
            "gender": r.gender,
            "age": r.age,
            "study_hours_per_day": r.study_hours_per_day,
            "attendance_percentage": r.attendance_percentage,
            "active_backlogs": r.active_backlogs,
            "academic_feedback": r.academic_feedback,
            "emotional_feedback": r.emotional_feedback,
            "sentiment_label": r.sentiment_label,
        }
        for r in records
    ]


def _chart_response(buffer, filename: str) -> StreamingResponse:
    """
    Wrap a BytesIO buffer in a StreamingResponse for PNG delivery.

    Sets appropriate headers so:
      - Browsers display the image directly (Content-Type: image/png)
      - The file has a meaningful name when downloaded (Content-Disposition)

    Args:
        buffer: BytesIO containing PNG image data
        filename: Suggested filename for download

    Returns:
        StreamingResponse that streams PNG bytes to the client
    """
    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename={filename}",
            "Cache-Control": "no-cache",
        },
    )


@router.get(
    "/sentiment-bar",
    summary="Sentiment distribution bar chart",
    description=(
        "Returns a PNG bar chart showing the count of students "
        "in each sentiment category (Positive, Neutral, Negative)."
    ),
    response_class=StreamingResponse,
    tags=["Visualisations"],
)
async def sentiment_bar_chart(db: Session = Depends(get_db)) -> StreamingResponse:
    """
    Generate and return a sentiment distribution bar chart.

    Opens directly as an image in the browser. Shows how many students
    fall into each sentiment category with count labels on each bar.
    """
    records = _get_all_records_as_dicts(db)
    buffer = viz_service.generate_sentiment_bar_chart(records)
    return _chart_response(buffer, "sentiment_bar_chart.png")


@router.get(
    "/sentiment-pie",
    summary="Sentiment distribution pie chart",
    description="Returns a PNG pie chart showing sentiment percentage breakdown.",
    response_class=StreamingResponse,
    tags=["Visualisations"],
)
async def sentiment_pie_chart(db: Session = Depends(get_db)) -> StreamingResponse:
    """Generate and return a sentiment distribution pie chart with percentages."""
    records = _get_all_records_as_dicts(db)
    buffer = viz_service.generate_sentiment_pie_chart(records)
    return _chart_response(buffer, "sentiment_pie_chart.png")


@router.get(
    "/attendance-vs-sentiment",
    summary="Attendance distribution by sentiment",
    description=(
        "Returns a PNG box plot showing how attendance percentage "
        "varies across sentiment categories."
    ),
    response_class=StreamingResponse,
    tags=["Visualisations"],
)
async def attendance_vs_sentiment(db: Session = Depends(get_db)) -> StreamingResponse:
    """
    Generate and return an attendance vs sentiment box plot.

    Reveals whether low-attendance students tend to have more
    negative sentiment — actionable insight for universities.
    """
    records = _get_all_records_as_dicts(db)
    buffer = viz_service.generate_attendance_vs_sentiment(records)
    return _chart_response(buffer, "attendance_vs_sentiment.png")


@router.get(
    "/backlogs-by-sentiment",
    summary="Backlog distribution by sentiment",
    description=(
        "Returns a PNG count plot showing backlog counts "
        "grouped by sentiment label."
    ),
    response_class=StreamingResponse,
    tags=["Visualisations"],
)
async def backlogs_by_sentiment(db: Session = Depends(get_db)) -> StreamingResponse:
    """Generate and return a backlogs distribution chart grouped by sentiment."""
    records = _get_all_records_as_dicts(db)
    buffer = viz_service.generate_backlogs_by_sentiment(records)
    return _chart_response(buffer, "backlogs_by_sentiment.png")


@router.get(
    "/gender-sentiment",
    summary="Sentiment breakdown by gender",
    description=(
        "Returns a PNG grouped bar chart showing sentiment "
        "distribution for each gender."
    ),
    response_class=StreamingResponse,
    tags=["Visualisations"],
)
async def gender_sentiment_chart(db: Session = Depends(get_db)) -> StreamingResponse:
    """Generate and return a gender vs sentiment grouped bar chart."""
    records = _get_all_records_as_dicts(db)
    buffer = viz_service.generate_gender_sentiment_chart(records)
    return _chart_response(buffer, "gender_sentiment.png")


@router.get(
    "/study-hours-distribution",
    summary="Study hours distribution by sentiment",
    description=(
        "Returns a PNG histogram showing study hours per day "
        "grouped by sentiment label."
    ),
    response_class=StreamingResponse,
    tags=["Visualisations"],
)
async def study_hours_distribution(db: Session = Depends(get_db)) -> StreamingResponse:
    """Generate and return a study hours distribution histogram by sentiment."""
    records = _get_all_records_as_dicts(db)
    buffer = viz_service.generate_study_hours_distribution(records)
    return _chart_response(buffer, "study_hours_distribution.png")