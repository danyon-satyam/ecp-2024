"""
Main application entry point.

On startup, create_tables() ensures all database tables exist.
This is safe to call every time — SQLAlchemy skips tables that
already exist.
"""
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import create_tables
from app.api.v1.endpoints.feedback import router as feedback_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(feedback_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables when the application starts."""
    create_tables()


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "message": f"{settings.app_name} is live"}