"""
Integration tests for Analytics API endpoints.

Tests ensure aggregation endpoints return correct structure
and meaningful data when records exist in the database.
"""
import pytest
from fastapi.testclient import TestClient


class TestSummaryEndpoint:
    """Tests for GET /api/v1/analytics/summary."""

    def test_summary_returns_200(self, client: TestClient):
        """Summary endpoint must return 200."""
        response = client.get("/api/v1/analytics/summary")
        assert response.status_code == 200

    def test_summary_contains_distribution(self, client: TestClient):
        """Response must contain sentiment_distribution key."""
        response = client.get("/api/v1/analytics/summary")
        data = response.json()
        assert "sentiment_distribution" in data

    def test_summary_reflects_submitted_records(
        self, client: TestClient, sample_feedback: dict
    ):
        """Summary total must increase after submitting feedback."""
        client.post("/api/v1/feedback", json=sample_feedback)
        response = client.get("/api/v1/analytics/summary")
        data = response.json()
        assert data["sentiment_distribution"]["total"] == 1


class TestBySentimentEndpoint:
    """Tests for GET /api/v1/analytics/by-sentiment."""

    def test_filter_positive_returns_200(self, client: TestClient):
        """Filtering by Positive must return 200."""
        response = client.get("/api/v1/analytics/by-sentiment?sentiment=Positive")
        assert response.status_code == 200

    def test_filter_invalid_sentiment_returns_422(self, client: TestClient):
        """Invalid sentiment value must return 422."""
        response = client.get("/api/v1/analytics/by-sentiment?sentiment=VeryHappy")
        assert response.status_code == 422

    def test_filter_returns_only_matching_records(
        self, client: TestClient, sample_feedback: dict, negative_feedback: dict
    ):
        """Filtering by Negative must return only Negative records."""
        client.post("/api/v1/feedback", json=sample_feedback)
        client.post("/api/v1/feedback", json=negative_feedback)
        response = client.get("/api/v1/analytics/by-sentiment?sentiment=Negative")
        data = response.json()
        for record in data["records"]:
            assert record["sentiment_label"] == "Negative"


class TestAtRiskEndpoint:
    """Tests for GET /api/v1/analytics/at-risk."""

    def test_at_risk_returns_200(self, client: TestClient):
        """At-risk endpoint must return 200."""
        response = client.get("/api/v1/analytics/at-risk")
        assert response.status_code == 200

    def test_at_risk_contains_required_keys(self, client: TestClient):
        """Response must contain total_at_risk and criteria keys."""
        response = client.get("/api/v1/analytics/at-risk")
        data = response.json()
        assert "total_at_risk" in data
        assert "criteria" in data
        assert "at_risk_percentage" in data

    def test_negative_student_appears_in_at_risk(
        self, client: TestClient, negative_feedback: dict
    ):
        """A student with Negative sentiment must appear in at-risk list."""
        client.post("/api/v1/feedback", json=negative_feedback)
        response = client.get("/api/v1/analytics/at-risk")
        data = response.json()
        assert data["total_at_risk"] >= 1


class TestTrendsEndpoint:
    """Tests for GET /api/v1/analytics/trends."""

    def test_trends_returns_200(self, client: TestClient):
        """Trends endpoint must return 200."""
        response = client.get("/api/v1/analytics/trends")
        assert response.status_code == 200

    def test_trends_contains_breakdown_keys(self, client: TestClient):
        """Response must contain all three breakdown categories."""
        response = client.get("/api/v1/analytics/trends")
        data = response.json()
        assert "by_gender" in data
        assert "by_academic_feedback" in data
        assert "by_emotional_feedback" in data