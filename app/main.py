"""
Main application entry point.

Tables are managed by Alembic migrations — run 'alembic upgrade head'.
ML model is loaded at startup — run 'python scripts/train_model.py'.
"""
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints.feedback import router as feedback_router
from app.api.v1.endpoints.analytics import router as analytics_router
from app.services.sentiment import get_model_info

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A production-grade REST API for analysing student sentiment "
        "at universities. Powered by CatBoost ML model trained on "
        "real university feedback data."
    ),
)

app.include_router(feedback_router, prefix=settings.api_v1_prefix)
app.include_router(analytics_router, prefix=f"{settings.api_v1_prefix}/analytics")


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """
    Health check endpoint — returns API and ML model status.

    Used by deployment systems, monitoring tools, and Swagger UI
    to verify the API and its ML components are operational.
    """
    model_info = get_model_info()
    return {
        "status": "ok",
        "message": f"{settings.app_name} is live",
        "version": settings.app_version,
        "ml_model": model_info,
    }