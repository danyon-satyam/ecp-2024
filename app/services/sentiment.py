"""
Sentiment Analysis Service — public interface for sentiment prediction.

This module is the single entry point for sentiment prediction across
the entire application. It delegates to the ML service transparently.

Why this indirection layer?
  The repository, endpoints, and tests all import calculate_sentiment()
  from here. If we ever swap CatBoost for a different model, or add
  an ensemble, we only change this file. Nothing else in the app changes.
  This is the Facade pattern — one clean interface hiding complexity behind it.
"""
from app.services.ml_model import sentiment_ml_service


def calculate_sentiment(emotional_feedback: str, academic_feedback: str) -> str:
    """
    Calculate the sentiment label for a student feedback record.

    Delegates to the ML service which uses the trained CatBoost model
    if available, or falls back to rule-based weighted scoring.

    Args:
        emotional_feedback: Student's emotional state (e.g. 'Happy', 'Sad')
        academic_feedback: Student's academic satisfaction (e.g. 'Good', 'Bad')

    Returns:
        Sentiment label: 'Positive', 'Neutral', or 'Negative'

    Example:
        >>> calculate_sentiment('Happy', 'Good')
        'Positive'
        >>> calculate_sentiment('Sad', 'Bad')
        'Negative'
    """
    return sentiment_ml_service.predict(emotional_feedback, academic_feedback)


def get_sentiment_summary(records: list[dict]) -> dict:
    """
    Generate sentiment distribution summary across a list of records.

    Args:
        records: List of feedback record dictionaries with 'sentiment_label' key

    Returns:
        Dictionary with counts and percentages for each sentiment label

    Example:
        >>> records = [{'sentiment_label': 'Positive'}, {'sentiment_label': 'Negative'}]
        >>> get_sentiment_summary(records)
        {'total': 2, 'positive': 1, 'positive_percentage': 50.0, ...}
    """
    total = len(records)
    if total == 0:
        return {
            "total": 0,
            "positive": 0, "positive_percentage": 0.0,
            "neutral": 0, "neutral_percentage": 0.0,
            "negative": 0, "negative_percentage": 0.0,
        }

    positive = sum(1 for r in records if r.get("sentiment_label") == "Positive")
    neutral = sum(1 for r in records if r.get("sentiment_label") == "Neutral")
    negative = sum(1 for r in records if r.get("sentiment_label") == "Negative")

    return {
        "total": total,
        "positive": positive,
        "positive_percentage": round((positive / total) * 100, 2),
        "neutral": neutral,
        "neutral_percentage": round((neutral / total) * 100, 2),
        "negative": negative,
        "negative_percentage": round((negative / total) * 100, 2),
    }


def get_model_info() -> dict:
    """
    Return information about the current prediction model.

    Returns:
        Dictionary with model type, mode, and readiness status
    """
    return sentiment_ml_service.get_model_info()