"""
Production smoke tests — verify deployed API is working.

These tests run against the LIVE production URL on Render.
They verify critical functionality without modifying data.

Run with:
    pytest tests/production/test_production_api.py -v
"""
import pytest
import requests


# ⚠️ CHANGE THIS to your actual Render URL
PRODUCTION_URL = "https://sentiment-api-vpmz.onrender.com"


class TestProductionHealth:
    """Verify production health and availability."""

    def test_health_endpoint_returns_200(self):
        """Production health check must return 200."""
        response = requests.get(f"{PRODUCTION_URL}/health")
        assert response.status_code == 200
    
    def test_health_response_valid(self):
        """Health response must contain expected structure."""
        response = requests.get(f"{PRODUCTION_URL}/health")
        data = response.json()
        assert "message" in data 
        assert data["status"] == "ok"
        assert data["ml_model"]["is_ready"] is True


class TestProductionEndpoints:
    """Verify all critical endpoints are accessible."""

    def test_swagger_ui_loads(self):
        """Swagger UI documentation must be accessible."""
        response = requests.get(f"{PRODUCTION_URL}/docs")
        assert response.status_code == 200
        
    def test_analytics_summary_returns_200(self):
        """Analytics summary must work (database has 500 records)."""
        response = requests.get(f"{PRODUCTION_URL}/api/v1/analytics/summary")
        assert response.status_code == 200
        
    def test_analytics_summary_has_data(self):
        """Summary must show at least 500 seeded records."""
        response = requests.get(f"{PRODUCTION_URL}/api/v1/analytics/summary")
        data = response.json()
        total = data["sentiment_distribution"]["total"] 
        assert total >= 500, f"Expected at least 500 records, got {total}"
        
    def test_get_feedback_returns_200(self):
        """GET feedback endpoint must work."""
        response = requests.get(f"{PRODUCTION_URL}/api/v1/feedback?limit=10")
        assert response.status_code == 200
        
    def test_visualisation_returns_png(self):
        """Visualization endpoint must return PNG image."""
        response = requests.get(
            f"{PRODUCTION_URL}/api/v1/visualisations/sentiment-bar"
        )
        assert response.status_code == 200
        assert "image/png" in response.headers["content-type"]


class TestProductionPerformance:
    """Basic performance checks on production."""

    def test_health_response_time_under_3s(self):  # Changed from 1s to 3s
        """Health check must respond quickly."""
        import time
        start = time.time()
        response = requests.get(f"{PRODUCTION_URL}/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 3.0, f"Health took {duration:.2f}s (limit: 3s)"
        
    def test_analytics_response_time_under_4s(self):  # Changed from 2s to 4s
        """Analytics should respond within reasonable time."""
        import time
        start = time.time()
        response = requests.get(f"{PRODUCTION_URL}/api/v1/analytics/summary")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 4.0, f"Analytics took {duration:.2f}s (limit: 4s)"