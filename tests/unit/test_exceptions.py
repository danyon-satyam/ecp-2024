"""
Unit tests for custom exception classes.

Tests ensure all exceptions produce the correct error codes,
status codes, and JSON-serialisable output.
"""
import pytest
from app.core.exceptions import (
    RecordNotFoundException,
    NoDataAvailableException,
    InvalidSentimentLabelException,
    ModelNotReadyException,
    SentimentAPIException,
)


class TestRecordNotFoundException:
    """Tests for RecordNotFoundException."""

    def test_correct_status_code(self):
        """Must return 404 status code."""
        exc = RecordNotFoundException(record_id=999)
        assert exc.status_code == 404

    def test_correct_error_code(self):
        """Must use RECORD_NOT_FOUND error code."""
        exc = RecordNotFoundException(record_id=999)
        assert exc.error_code == "RECORD_NOT_FOUND"

    def test_message_contains_id(self):
        """Error message must include the requested ID."""
        exc = RecordNotFoundException(record_id=42)
        assert "42" in exc.message

    def test_to_dict_contains_required_keys(self):
        """to_dict() must contain all standard error response keys."""
        exc = RecordNotFoundException(record_id=1)
        result = exc.to_dict()
        assert "error_code" in result
        assert "message" in result
        assert "status_code" in result
        assert "timestamp" in result

    def test_is_subclass_of_base_exception(self):
        """Must inherit from SentimentAPIException."""
        exc = RecordNotFoundException(record_id=1)
        assert isinstance(exc, SentimentAPIException)


class TestNoDataAvailableException:
    """Tests for NoDataAvailableException."""

    def test_correct_status_code(self):
        """Must return 404 status code."""
        exc = NoDataAvailableException()
        assert exc.status_code == 404

    def test_correct_error_code(self):
        """Must use NO_DATA_AVAILABLE error code."""
        exc = NoDataAvailableException()
        assert exc.error_code == "NO_DATA_AVAILABLE"


class TestInvalidSentimentLabelException:
    """Tests for InvalidSentimentLabelException."""

    def test_correct_status_code(self):
        """Must return 422 status code."""
        exc = InvalidSentimentLabelException("VeryHappy")
        assert exc.status_code == 422

    def test_message_contains_invalid_label(self):
        """Error message must include the invalid label provided."""
        exc = InvalidSentimentLabelException("VeryHappy")
        assert "VeryHappy" in exc.message


class TestModelNotReadyException:
    """Tests for ModelNotReadyException."""

    def test_correct_status_code(self):
        """Must return 503 Service Unavailable."""
        exc = ModelNotReadyException()
        assert exc.status_code == 503

    def test_correct_error_code(self):
        """Must use MODEL_NOT_READY error code."""
        exc = ModelNotReadyException()
        assert exc.error_code == "MODEL_NOT_READY"


class TestErrorHandlerIntegration:
    """Integration tests for global error handlers via the API."""

    def test_404_returns_standard_error_format(self, client):
        """404 errors must return our standard error JSON format."""
        response = client.get("/api/v1/feedback/99999")
        assert response.status_code == 404
        data = response.json()
        assert "error_code" in data
        assert "message" in data
        assert "timestamp" in data
        assert data["error_code"] == "RECORD_NOT_FOUND"

    def test_validation_error_returns_errors_list(self, client):
        """422 validation errors must include field-level errors list."""
        response = client.post(
            "/api/v1/feedback",
            json={"invalid": "data"},
        )
        assert response.status_code == 422
        data = response.json()
        assert "errors" in data
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_404_includes_path(self, client):
        """404 response must include the request path."""
        response = client.get("/api/v1/feedback/99999")
        data = response.json()
        assert "path" in data