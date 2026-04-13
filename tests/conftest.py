"""
Pytest configuration and shared fixtures.

conftest.py is automatically loaded by Pytest before running any tests.
Fixtures defined here are available to ALL test files without importing them.

A fixture is a reusable piece of setup code. For example, instead of
creating a test client in every single test function, we define it once
here and Pytest injects it automatically wherever it is needed.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints.feedback import feedback_store


@pytest.fixture
def client() -> TestClient:
    """
    Create a fresh FastAPI TestClient for each test.

    TestClient simulates HTTP requests to your API without needing
    a running server. It is fast, isolated, and perfect for testing.

    Yields the client, then clears the feedback_store after each test
    so tests do not interfere with each other. This is called teardown.
    """
    with TestClient(app) as test_client:
        yield test_client
    # Teardown: clear all records after every test so each test starts fresh
    feedback_store.clear()


@pytest.fixture
def sample_feedback() -> dict:
    """
    A valid sample feedback payload for reuse across tests.

    Instead of copy-pasting this dictionary in every test,
    we define it once here. If we need to change the structure
    later, we change it in one place only.
    """
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
    """A valid feedback payload that should produce a Negative sentiment."""
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