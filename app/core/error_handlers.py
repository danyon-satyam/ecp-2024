"""
Global exception handlers registered with the FastAPI application.

These handlers intercept exceptions ANYWHERE in the request lifecycle
and convert them to consistent JSON error responses.

Why global handlers instead of try/except in each endpoint?
  Without global handlers, every endpoint needs its own try/except block.
  That is 20+ blocks of identical error-catching code — a maintenance
  nightmare. Global handlers follow the DRY principle (Don't Repeat Yourself).

  Every error, whether it is our custom SentimentAPIException, a Pydantic
  validation error, or an unexpected crash, returns the same JSON structure.
  Client developers can write one error-handling function for all cases.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime

from app.core.exceptions import SentimentAPIException


def register_error_handlers(app: FastAPI) -> None:
    """
    Register all global exception handlers with the FastAPI app.

    Called once during application startup in main.py.

    Args:
        app: The FastAPI application instance
    """

    @app.exception_handler(SentimentAPIException)
    async def sentiment_api_exception_handler(
        request: Request, exc: SentimentAPIException
    ) -> JSONResponse:
        """
        Handle all SentimentAPIException subclasses.

        Converts our domain exceptions to structured JSON responses.
        Includes the request path for easier debugging in logs.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                **exc.to_dict(),
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors (422 Unprocessable Entity).

        FastAPI's default 422 response is verbose and inconsistent
        with our error format. This handler reformats it to match
        our standard structure while keeping the field-level detail.
        """
        errors = []
        for error in exc.errors():
            field = " → ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "issue": error["msg"],
                "invalid_value": error.get("input"),
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error_code": "VALIDATION_ERROR",
                "message": "Request data failed validation. Check the errors list.",
                "status_code": 422,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path),
                "errors": errors,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Handle any unhandled exception (catch-all for 500 errors).

        IMPORTANT: Never expose internal error details (stack traces,
        file paths, variable values) to the client. This is a security
        requirement — implementation details help attackers.

        The internal error is logged (would go to Cloud Logging on GCP)
        while the client receives only a generic safe message.
        """
        # In production this would use a proper logger (e.g. structlog)
        print(f"UNHANDLED ERROR on {request.url.path}: {type(exc).__name__}: {exc}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": (
                    "An unexpected error occurred. "
                    "Please try again or contact support."
                ),
                "status_code": 500,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path),
            },
        )