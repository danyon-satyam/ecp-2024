"""
Database connection and session management.

Updated for production-grade connection pooling and async-compatible
session handling via FastAPI's thread pool integration.

Key concepts:
  - Connection Pool: instead of opening a new database connection per
    request (slow, expensive), we maintain a pool of reusable connections.
    SQLAlchemy's pool_size controls how many simultaneous connections exist.

  - pool_size=10: up to 10 simultaneous database connections.
    For 100 concurrent users this is sufficient because most requests
    complete in <50ms — connections are recycled very quickly.

  - max_overflow=20: if all 10 connections are busy, allow 20 more
    temporary connections. Total maximum = 30 connections under peak load.

  - pool_recycle=3600: recycle connections after 1 hour to prevent
    PostgreSQL's idle connection timeout from causing errors.

  - pool_pre_ping=True: before using a pooled connection, send a quick
    ping to verify it is still alive. Prevents "connection lost" errors
    after idle periods.

Why not full async SQLAlchemy?
  Full async SQLAlchemy (with asyncpg) requires rewriting all ORM queries
  with async/await syntax. For this project scale, running synchronous
  SQLAlchemy in FastAPI's thread pool (via Depends) achieves equivalent
  concurrency benefits with much less code complexity.
  Full async is appropriate when queries take >100ms regularly.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator

from app.core.config import settings
from app.models.student_feedback import Base


def _build_engine():
    """
    Build the SQLAlchemy engine with production-grade pool settings.

    Separates engine creation into a function so tests can override
    the database URL without affecting the module-level engine.
    """
    return create_engine(
        settings.database_url,
        # Connection pool configuration
        poolclass=QueuePool,
        pool_size=10,           # Maintain 10 persistent connections
        max_overflow=20,        # Allow 20 extra connections under peak load
        pool_recycle=3600,      # Recycle connections after 1 hour
        pool_pre_ping=True,     # Verify connection health before use
        pool_timeout=30,        # Wait max 30s for a free connection
        # Never echo SQL in production — massive performance hit under load
        echo=False,
    )


engine = _build_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def create_tables() -> None:
    """
    Create all database tables if they do not exist.

    Only used in testing with SQLite. Production uses Alembic migrations.
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency providing a database session per request.

    FastAPI automatically runs this in a thread pool when used with
    async endpoint functions — meaning database I/O does not block
    the async event loop. This is how sync SQLAlchemy works safely
    with async FastAPI.

    Usage in endpoints:
        async def my_endpoint(db: Session = Depends(get_db)):
            ...

    The session is always closed after the request, even on errors,
    preventing connection leaks under sustained load.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()