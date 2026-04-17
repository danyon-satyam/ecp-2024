"""
Database connection and session management.

This module sets up the SQLAlchemy engine and session factory.

Key concepts:
  - Engine: the connection to the database (like opening a pipe to PostgreSQL)
  - SessionLocal: a factory that creates database sessions
  - Session: a unit of work — one session per request, closed after

Why one session per request?
  Because a session holds a database connection open. If we kept one
  session forever, we'd run out of connections under heavy load.
  FastAPI's dependency injection (Depends) handles opening and closing
  sessions automatically for each request.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings
from app.models.feedback import Base


# Create the database engine
# pool_pre_ping=True: checks the connection is alive before using it
# This prevents "connection lost" errors after idle periods
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

# Session factory — call SessionLocal() to get a new session
SessionLocal = sessionmaker(
    autocommit=False,  # We control commits manually (safer)
    autoflush=False,   # We control flushes manually
    bind=engine,
)


def create_tables() -> None:
    """
    Create all database tables if they do not exist.

    Called once at application startup. Safe to call multiple times —
    SQLAlchemy checks if tables already exist before creating them.
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request.

    Usage in endpoints:
        def my_endpoint(db: Session = Depends(get_db)):
            ...

    The 'yield' makes this a context manager:
      - Opens a session before the endpoint runs
      - Closes the session after the endpoint finishes (even on errors)
    This prevents connection leaks under heavy load.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()