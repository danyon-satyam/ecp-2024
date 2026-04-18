"""
Unit tests for the sentiment analysis service.

These tests work in BOTH modes:
  - With ML model loaded (production)
  - With rule-based fallback (CI, development before training)

We test the PUBLIC interface (calculate_sentiment) not the internal
ML or rule-based implementation. This means tests pass regardless
of which prediction mode is active — a key principle of good testing.
"""
import pytest
from app.services.sentiment import calculate_sentiment, get_sentiment_summary


class TestCalculateSentiment:
    """Tests for the calculate_sentiment() public interface."""

    def test_happy_good_returns_positive(self):
        """Happy + Good must always return Positive."""
        assert calculate_sentiment("Happy", "Good") == "Positive"

    def test_glad_excellent_returns_positive(self):
        """Glad + Excellent must always return Positive."""
        assert calculate_sentiment("Glad", "Excellent") == "Positive"

    def test_sad_bad_returns_negative(self):
        """Sad + Bad must always return Negative."""
        assert calculate_sentiment("Sad", "Bad") == "Negative"

    def test_angry_bad_returns_negative(self):
        """Angry + Bad must always return Negative."""
        assert calculate_sentiment("Angry", "Bad") == "Negative"

    def test_neutral_satisfactory_returns_neutral(self):
        """Neutral + Satisfactory must always return Neutral."""
        assert calculate_sentiment("Neutral", "Satisfactory") == "Neutral"

    def test_return_type_is_always_string(self):
        """Return type must always be a string."""
        result = calculate_sentiment("Happy", "Good")
        assert isinstance(result, str)

    def test_return_value_is_valid_label(self):
        """Return value must always be one of three valid labels."""
        valid = {"Positive", "Neutral", "Negative"}
        assert calculate_sentiment("Happy", "Good") in valid
        assert calculate_sentiment("Sad", "Bad") in valid
        assert calculate_sentiment("Neutral", "Satisfactory") in valid

    def test_unknown_input_does_not_crash(self):
        """Unknown values must not raise exceptions — return a valid label."""
        result = calculate_sentiment("Unknown", "Unknown")
        assert result in {"Positive", "Neutral", "Negative"}


class TestGetSentimentSummary:
    """Tests for get_sentiment_summary() aggregation function."""

    def test_empty_records_returns_zero_counts(self):
        """Empty list must return all zeros without dividing by zero."""
        result = get_sentiment_summary([])
        assert result["total"] == 0
        assert result["positive"] == 0

    def test_correct_counts_with_mixed_records(self):
        """Counts must reflect the actual sentiment distribution."""
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

    def test_percentages_add_up_to_100(self):
        """Positive + Neutral + Negative percentages must sum to 100."""
        records = [
            {"sentiment_label": "Positive"},
            {"sentiment_label": "Negative"},
            {"sentiment_label": "Neutral"},
            {"sentiment_label": "Positive"},
        ]
        result = get_sentiment_summary(records)
        total = (
            result["positive_percentage"]
            + result["neutral_percentage"]
            + result["negative_percentage"]
        )
        assert round(total, 1) == 100.0