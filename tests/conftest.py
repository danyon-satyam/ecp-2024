"""
Pytest configuration and shared fixtures.

For testing we use SQLite (an in-memory database) instead of PostgreSQL.
Why? Because:
  - SQLite needs zero setup — no server, no credentials
  - Each test run gets a completely fresh database
  - Tests run in milliseconds
  - The real PostgreSQL is never touched by tests

This is called a Test Double — a safe replacement for the real dependency.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.core.database import get_db
from app.models.student_feedback import Base

# SQLite in-memory database — exists only during the test session
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """
    Create all tables before each test, drop them after.

    scope="function" means this runs fresh for EVERY test function.
    This guarantees tests never share database state.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Session:
    """Provide a clean database session for each test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> TestClient:
    """
    Create a TestClient that uses the SQLite test database.

    We override FastAPI's get_db dependency to inject the test
    database session instead of the real PostgreSQL session.
    This is called Dependency Injection — a core FastAPI feature.
    """
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_feedback() -> dict:
    """Valid sample feedback payload for reuse across tests."""
    return {
        "roll_number": "CS2021001",
        "gender": "Male",
        "age": 20,
        "study_hours_per_day": 6,
        "attendance_percentage": 85,
        "active_backlogs": 0,
        "academic_feedback": "Good",
        "emotional_feedback": "Happy",
    }


@pytest.fixture
def negative_feedback() -> dict:
    """Feedback payload that produces Negative sentiment."""
    return {
        "roll_number": "CS2021002",
        "gender": "Female",
        "age": 21,
        "study_hours_per_day": 3,
        "attendance_percentage": 60,
        "active_backlogs": 2,
        "academic_feedback": "Bad",
        "emotional_feedback": "Sad",
    }