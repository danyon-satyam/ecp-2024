"""
Main application entry point.

Tables are managed by Alembic migrations — not created at startup.
To apply migrations: alembic upgrade head
To create a new migration: alembic revision --autogenerate -m "description"
"""
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints.feedback import router as feedback_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A production-grade API to analyse student sentiment at universities.",
)

app.include_router(feedback_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Health check endpoint — used by deployment systems to verify the API is live."""
    return {"status": "ok", "message": f"{settings.app_name} is live"}