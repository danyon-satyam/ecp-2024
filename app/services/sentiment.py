"""
Sentiment Analysis Service.

This module contains the core business logic for calculating
student sentiment scores. Keeping this separate from the API layer
means we can reuse it anywhere (API, scripts, tests) and swap
out the ML model later without touching the API code.
"""


# Sentiment mappings based on our domain knowledge from the notebook
EMOTIONAL_SENTIMENT_MAP = {
    "Happy": 1,
    "Glad": 1,
    "Neutral": 0,
    "Sad": -1,
    "Angry": -1,
}

ACADEMIC_SENTIMENT_MAP = {
    "Excellent": 1,
    "Good": 1,
    "Satisfactory": 0,
    "Bad": -1,
}

# Weights from our notebook analysis (emotional carries more weight)
WEIGHT_EMOTIONAL = 0.7
WEIGHT_ACADEMIC = 0.3


def calculate_sentiment(emotional_feedback: str, academic_feedback: str) -> str:
    """
    Calculate overall sentiment label for a student.

    Uses a weighted combination of emotional and academic feedback
    scores, matching the methodology from the research notebook.

    Args:
        emotional_feedback: Student's emotional state (e.g. 'Happy', 'Sad')
        academic_feedback: Student's academic satisfaction (e.g. 'Good', 'Bad')

    Returns:
        A sentiment label string: 'Positive', 'Neutral', or 'Negative'
    """
    emotional_score = EMOTIONAL_SENTIMENT_MAP.get(emotional_feedback, 0)
    academic_score = ACADEMIC_SENTIMENT_MAP.get(academic_feedback, 0)

    weighted_score = (
        WEIGHT_EMOTIONAL * emotional_score + WEIGHT_ACADEMIC * academic_score
    )

    if weighted_score > 0:
        return "Positive"
    elif weighted_score < 0:
        return "Negative"
    else:
        return "Neutral"


def get_sentiment_summary(records: list[dict]) -> dict:
    """
    Generate a summary of sentiment distribution across all records.

    Args:
        records: List of all feedback records

    Returns:
        A dictionary with counts and percentages for each sentiment label
    """
    total = len(records)
    if total == 0:
        return {"total": 0, "positive": 0, "neutral": 0, "negative": 0}

    positive = sum(1 for r in records if r["sentiment_label"] == "Positive")
    neutral = sum(1 for r in records if r["sentiment_label"] == "Neutral")
    negative = sum(1 for r in records if r["sentiment_label"] == "Negative")

    return {
        "total": total,
        "positive": positive,
        "positive_percentage": round((positive / total) * 100, 2),
        "neutral": neutral,
        "neutral_percentage": round((neutral / total) * 100, 2),
        "negative": negative,
        "negative_percentage": round((negative / total) * 100, 2),
    }