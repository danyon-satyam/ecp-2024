"""
Custom exception classes for the Student Sentiment API.

Why custom exceptions instead of using HTTPException directly?

1. Consistency: Every error response across the entire API has
   the same JSON structure — clients never need to guess the format.

2. Separation: Business logic raises domain exceptions (RecordNotFound,
   InvalidSentimentLabel). The API layer catches them and converts to
   HTTP responses. Domain code never needs to know about HTTP.

3. Debuggability: Custom exceptions carry more context than a plain
   string message — error codes, timestamps, and request details
   make production debugging much faster.

Standard error response format:
{
    "error_code": "RECORD_NOT_FOUND",
    "message": "Feedback record with ID 999 not found.",
    "status_code": 404,
    "timestamp": "2026-04-12T10:30:00"
}
"""
from datetime import datetime


class SentimentAPIException(Exception):
    """
    Base exception for all Student Sentiment API errors.

    All custom exceptions inherit from this so callers can catch
    all API-specific errors with a single except clause.
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
    ) -> None:
        """
        Initialise the exception.

        Args:
            message: Human-readable error description
            error_code: Machine-readable error identifier (SCREAMING_SNAKE_CASE)
            status_code: HTTP status code to return to the client
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to the standard API error response dict."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "timestamp": self.timestamp,
        }


class RecordNotFoundException(SentimentAPIException):
    """Raised when a requested database record does not exist."""

    def __init__(self, record_id: int) -> None:
        super().__init__(
            message=f"Feedback record with ID {record_id} not found.",
            error_code="RECORD_NOT_FOUND",
            status_code=404,
        )


class NoDataAvailableException(SentimentAPIException):
    """Raised when an operation requires data but none exists yet."""

    def __init__(self, operation: str = "this operation") -> None:
        super().__init__(
            message=(
                f"No student feedback data available for {operation}. "
                "Please submit feedback records first."
            ),
            error_code="NO_DATA_AVAILABLE",
            status_code=404,
        )


class InvalidSentimentLabelException(SentimentAPIException):
    """Raised when an invalid sentiment label is provided."""

    def __init__(self, label: str) -> None:
        super().__init__(
            message=(
                f"'{label}' is not a valid sentiment label. "
                "Valid options are: Positive, Neutral, Negative."
            ),
            error_code="INVALID_SENTIMENT_LABEL",
            status_code=422,
        )


class ModelNotReadyException(SentimentAPIException):
    """Raised when the ML model is requested but not loaded."""

    def __init__(self) -> None:
        super().__init__(
            message=(
                "ML model is not loaded. "
                "Run 'python scripts/train_model.py' to train the model."
            ),
            error_code="MODEL_NOT_READY",
            status_code=503,
        )