"""
Main application entry point.

This module initialises the FastAPI application and registers all routers.
"""
from fastapi import FastAPI
from app.api.v1.endpoints.feedback import router as feedback_router

app = FastAPI(
    title="Student Sentiment Analysis API",
    description="A production-grade API to analyse student feedback and emotional sentiment at universities.",
    version="0.1.0",
)

app.include_router(feedback_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.

    Returns the current status of the API.
    This is used by deployment systems to verify the server is running.
    """
    return {"status": "ok", "message": "Student Sentiment API is live"}