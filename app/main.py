"""
Main application entry point.

This module initialises the FastAPI application and registers all routers.
"""
from fastapi import FastAPI

app = FastAPI(
    title="Student Sentiment Analysis API",
    description="Analyse student feedback and emotional sentiment at scale.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "ok", "message": "Student Sentiment API is live"}