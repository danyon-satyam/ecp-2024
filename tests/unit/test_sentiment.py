"""
Unit tests for the sentiment analysis service.

Unit tests focus on testing ONE function in complete isolation.
We do not start the API server, we do not touch the database —
we just call the function directly and check the output.

TDD mindset for this file:
  - We know exactly what calculate_sentiment() should return for each input
  - We write those expectations as tests
  - If the function ever breaks, these tests tell us immediately
"""
import pytest
from app.services.sentiment import calculate_sentiment, get_sentiment_summary


class TestCalculateSentiment:
    """
    Tests for the calculate_sentiment() function.

    We group related tests inside a class. This keeps the test file
    organised and makes the Pytest output easier to read.
    """

    def test_positive_sentiment_happy_good(self):
        """Happy + Good should produce Positive sentiment."""
        result = calculate_sentiment(
            emotional_feedback="Happy",
            academic_feedback="Good"
        )
        assert result == "Positive"

    def test_positive_sentiment_glad_excellent(self):
        """Glad + Excellent should produce Positive sentiment."""
        result = calculate_sentiment(
            emotional_feedback="Glad",
            academic_feedback="Excellent"
        )
        assert result == "Positive"

    def test_negative_sentiment_sad_bad(self):
        """Sad + Bad should produce Negative sentiment."""
        result = calculate_sentiment(
            emotional_feedback="Sad",
            academic_feedback="Bad"
        )
        assert result == "Negative"

    def test_negative_sentiment_angry_bad(self):
        """Angry + Bad should produce Negative sentiment."""
        result = calculate_sentiment(
            emotional_feedback="Angry",
            academic_feedback="Bad"
        )
        assert result == "Negative"

    def test_neutral_sentiment(self):
        """Neutral + Satisfactory should produce Neutral sentiment."""
        result = calculate_sentiment(
            emotional_feedback="Neutral",
            academic_feedback="Satisfactory"
        )
        assert result == "Neutral"

    def test_mixed_positive_dominates(self):
        """
        Happy (weight 0.7) + Bad (weight 0.3) should be Positive.

        This tests our weighted scoring: 0.7*1 + 0.3*(-1) = 0.4 > 0
        So emotional state dominates when there is a conflict.
        """
        result = calculate_sentiment(
            emotional_feedback="Happy",
            academic_feedback="Bad"
        )
        assert result == "Positive"

    def test_unknown_values_default_to_neutral(self):
        """
        Unknown feedback values should default to Neutral (score 0).

        This tests the .get(key, 0) default in our service.
        Real-world data can be messy — this protects against crashes.
        """
        result = calculate_sentiment(
            emotional_feedback="Unknown",
            academic_feedback="Unknown"
        )
        assert result == "Neutral"

    def test_return_type_is_string(self):
        """The function must always return a string, never None or a number."""
        result = calculate_sentiment("Happy", "Good")
        assert isinstance(result, str)

    def test_return_value_is_valid_label(self):
        """The result must always be one of the three valid labels."""
        valid_labels = {"Positive", "Neutral", "Negative"}
        result = calculate_sentiment("Happy", "Good")
        assert result in valid_labels


class TestGetSentimentSummary:
    """Tests for the get_sentiment_summary() aggregation function."""

    def test_empty_records_returns_zero_counts(self):
        """An empty list should return all zeros — no division errors."""
        result = get_sentiment_summary([])
        assert result["total"] == 0
        assert result["positive"] == 0
        assert result["negative"] == 0

    def test_correct_counts_with_mixed_records(self):
        """Summary should count each sentiment label correctly."""
        records = [
            {"sentiment_label": "Positive"},
            {"sentiment_label": "Positive"},
            {"sentiment_label": "Negative"},
            {"sentiment_label": "Neutral"},
        ]
        result = get_sentiment_summary(records)
        assert result["total"] == 4
        assert result["positive"] == 2
        assert result["negative"] == 1
        assert result["neutral"] == 1

    def test_percentages_sum_to_100(self):
        """Positive + Neutral + Negative percentages must sum to 100."""
        records = [
            {"sentiment_label": "Positive"},
            {"sentiment_label": "Negative"},
            {"sentiment_label": "Neutral"},
            {"sentiment_label": "Positive"},
        ]
        result = get_sentiment_summary(records)
        total_pct = (
            result["positive_percentage"]
            + result["neutral_percentage"]
            + result["negative_percentage"]
        )
        assert round(total_pct, 1) == 100.0