"""
Main application entry point.

Setup order:
  1. alembic upgrade head     — apply database migrations
  2. python scripts/train_model.py  — train ML model
  3. python scripts/seed_database.py — seed with mock data
  4. uvicorn app.main:app --reload  — start API server
"""
from fastapi import FastAPI
from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.api.v1.endpoints.feedback import router as feedback_router
from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.visualisations import router as viz_router
from app.services.sentiment import get_model_info
import logging
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A production-grade REST API for analysing student sentiment "
        "at universities. Powered by CatBoost ML model."
    ),
)

# Register global exception handlers — must be before routers
register_error_handlers(app)

app.include_router(feedback_router, prefix=settings.api_v1_prefix)
app.include_router(
    analytics_router,
    prefix=f"{settings.api_v1_prefix}/analytics",
)
app.include_router(
    viz_router,
    prefix=f"{settings.api_v1_prefix}/visualisations",
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check — returns API and ML model status."""
    return {
        "status": "ok",
        "message": f"{settings.app_name} is live",
        "version": settings.app_version,
        "ml_model": get_model_info(),
    }


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("=" * 60)
    logger.info("🚀 Student Sentiment API Starting")
    logger.info(f"   App Name: {settings.app_name}")
    logger.info(f"   Debug Mode: {settings.debug}")
    logger.info(f"   API Prefix: {settings.api_v1_prefix}")
    logger.info(f"   Database: PostgreSQL (Render Managed)")
    logger.info(f"   ML Model: CatBoost Loaded")
    logger.info(f"   Deployment: Production (Render.com)")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("🛑 Student Sentiment API Shutting Down")    