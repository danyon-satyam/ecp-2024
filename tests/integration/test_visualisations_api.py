"""
Integration tests for Visualisation API endpoints.

Visualisation endpoints return PNG images — not JSON.
Tests verify the correct content type, status codes,
and that the response contains actual image data.
"""
import pytest
from fastapi.testclient import TestClient


def _seed_test_records(client: TestClient, sample: dict, negative: dict) -> None:
    """Helper to submit two test records before chart tests."""
    client.post("/api/v1/feedback", json=sample)
    client.post("/api/v1/feedback", json=negative)


class TestSentimentBarChart:
    """Tests for GET /api/v1/visualisations/sentiment-bar."""

    def test_returns_200_with_data(
        self, client: TestClient, sample_feedback: dict, negative_feedback: dict
    ):
        """Bar chart endpoint must return 200 when data exists."""
        _seed_test_records(client, sample_feedback, negative_feedback)
        response = client.get("/api/v1/visualisations/sentiment-bar")
        assert response.status_code == 200

    def test_returns_png_content_type(
        self, client: TestClient, sample_feedback: dict, negative_feedback: dict
    ):
        """Response Content-Type must be image/png."""
        _seed_test_records(client, sample_feedback, negative_feedback)
        response = client.get("/api/v1/visualisations/sentiment-bar")
        assert "image/png" in response.headers["content-type"]

    def test_returns_non_empty_image(
        self, client: TestClient, sample_feedback: dict, negative_feedback: dict
    ):
        """Response body must contain actual image bytes (not empty)."""
        _seed_test_records(client, sample_feedback, negative_feedback)
        response = client.get("/api/v1/visualisations/sentiment-bar")
        assert len(response.content) > 1000  # PNG files are always > 1KB

    def test_returns_404_when_no_data(self, client: TestClient):
        """Bar chart must return 404 when no records exist."""
        response = client.get("/api/v1/visualisations/sentiment-bar")
        assert response.status_code == 404


class TestSentimentPieChart:
    """Tests for GET /api/v1/visualisations/sentiment-pie."""

    def test_returns_200_with_data(
        self, client: TestClient, sample_feedback: dict, negative_feedback: dict
    ):
        """Pie chart endpoint must return 200 when data exists."""
        _seed_test_records(client, sample_feedback, negative_feedback)
        response = client.get("/api/v1/visualisations/sentiment-pie")
        assert response.status_code == 200

    def test_returns_png_content_type(
        self, client: TestClient, sample_feedback: dict, negative_feedback: dict
    ):
        """Pie chart response Content-Type must be image/png."""
        _seed_test_records(client, sample_feedback, negative_feedback)
        response = client.get("/api/v1/visualisations/sentiment-pie")
        assert "image/png" in response.headers["content-type"]


class TestAttendanceVsSentiment:
    """Tests for GET /api/v1/visualisations/attendance-vs-sentiment."""

    def test_returns_200_with_data(
        self, client: TestClient, sample_feedback: dict, negative_feedback: dict
    ):
        """Attendance chart must return 200 when data exists."""
        _seed_test_records(client, sample_feedback, negative_feedback)
        response = client.get("/api/v1/visualisations/attendance-vs-sentiment")
        assert response.status_code == 200

    def test_returns_404_when_no_data(self, client: TestClient):
        """Must return 404 when no records exist."""
        response = client.get("/api/v1/visualisations/attendance-vs-sentiment")
        assert response.status_code == 404


class TestAllVisualisationEndpoints:
    """Smoke tests — all 6 chart endpoints return 200 when data exists."""

    CHART_ENDPOINTS = [
        "/api/v1/visualisations/sentiment-bar",
        "/api/v1/visualisations/sentiment-pie",
        "/api/v1/visualisations/attendance-vs-sentiment",
        "/api/v1/visualisations/backlogs-by-sentiment",
        "/api/v1/visualisations/gender-sentiment",
        "/api/v1/visualisations/study-hours-distribution",
    ]

    def test_all_chart_endpoints_return_200(
        self, client: TestClient, sample_feedback: dict, negative_feedback: dict
    ):
        """Every chart endpoint must return 200 when records exist."""
        _seed_test_records(client, sample_feedback, negative_feedback)
        for endpoint in self.CHART_ENDPOINTS:
            response = client.get(endpoint)
            assert response.status_code == 200, (
                f"Expected 200 from {endpoint}, got {response.status_code}"
            )

    def test_all_chart_endpoints_return_png(
        self, client: TestClient, sample_feedback: dict, negative_feedback: dict
    ):
        """Every chart endpoint must return image/png Content-Type."""
        _seed_test_records(client, sample_feedback, negative_feedback)
        for endpoint in self.CHART_ENDPOINTS:
            response = client.get(endpoint)
            assert "image/png" in response.headers.get("content-type", ""), (
                f"Expected image/png from {endpoint}"
            )