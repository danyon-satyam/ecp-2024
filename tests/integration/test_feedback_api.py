"""
Integration tests for the Student Feedback API endpoints.

Integration tests test the FULL flow: HTTP request → router → service → response.
We use FastAPI's TestClient which simulates real HTTP calls without a server.

Each test function name starts with test_ (Pytest requirement).
Each test function tests ONE specific behaviour — not multiple things at once.
This makes failures easy to diagnose: if test_submit_feedback_returns_201 fails,
you know exactly what broke.
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check_returns_200(self, client: TestClient):
        """Health endpoint must return HTTP 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_ok_status(self, client: TestClient):
        """Health endpoint must return status: ok in the body."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"


class TestSubmitFeedback:
    """Tests for POST /api/v1/feedback (Create operation)."""

    def test_submit_feedback_returns_201(self, client: TestClient, sample_feedback: dict):
        """
        Successful feedback submission must return HTTP 201 Created.

        201 means a new resource was created — this is the correct
        REST standard for POST requests that create records.
        """
        response = client.post("/api/v1/feedback", json=sample_feedback)
        assert response.status_code == 201

    def test_submit_feedback_returns_positive_sentiment(
        self, client: TestClient, sample_feedback: dict
    ):
        """Happy + Good feedback must result in Positive sentiment label."""
        response = client.post("/api/v1/feedback", json=sample_feedback)
        data = response.json()
        assert data["sentiment_label"] == "Positive"

    def test_submit_negative_feedback_returns_negative_sentiment(
        self, client: TestClient, negative_feedback: dict
    ):
        """Sad + Bad feedback must result in Negative sentiment label."""
        response = client.post("/api/v1/feedback", json=negative_feedback)
        data = response.json()
        assert data["sentiment_label"] == "Negative"

    def test_submit_feedback_assigns_id(self, client: TestClient, sample_feedback: dict):
        """Each submitted record must receive a unique auto-generated ID."""
        response = client.post("/api/v1/feedback", json=sample_feedback)
        data = response.json()
        assert "id" in data
        assert data["id"] == 1

    def test_submit_second_feedback_gets_id_2(
        self, client: TestClient, sample_feedback: dict, negative_feedback: dict
    ):
        """Second submitted record must receive ID 2."""
        client.post("/api/v1/feedback", json=sample_feedback)
        response = client.post("/api/v1/feedback", json=negative_feedback)
        data = response.json()
        assert data["id"] == 2

    def test_submit_invalid_gender_returns_422(
        self, client: TestClient, sample_feedback: dict
    ):
        """
        Sending an invalid gender value must return HTTP 422 Unprocessable Entity.

        422 means the data failed validation. Pydantic catches this automatically.
        This test proves our validation is working correctly.
        """
        sample_feedback["gender"] = "InvalidGender"
        response = client.post("/api/v1/feedback", json=sample_feedback)
        assert response.status_code == 422

    def test_submit_invalid_emotional_feedback_returns_422(
        self, client: TestClient, sample_feedback: dict
    ):
        """An emotional feedback value not in the allowed list must return 422."""
        sample_feedback["emotional_feedback"] = "Ecstatic"
        response = client.post("/api/v1/feedback", json=sample_feedback)
        assert response.status_code == 422

    def test_submit_age_below_minimum_returns_422(
        self, client: TestClient, sample_feedback: dict
    ):
        """Age below 17 must be rejected with 422."""
        sample_feedback["age"] = 10
        response = client.post("/api/v1/feedback", json=sample_feedback)
        assert response.status_code == 422

    def test_submit_missing_required_field_returns_422(self, client: TestClient):
        """Sending incomplete data (missing roll_number) must return 422."""
        incomplete = {"gender": "Male", "age": 20}
        response = client.post("/api/v1/feedback", json=incomplete)
        assert response.status_code == 422


class TestGetFeedback:
    """Tests for GET /api/v1/feedback (Read All operation)."""

    def test_get_all_feedback_empty_returns_200(self, client: TestClient):
        """GET all feedback on empty store must return 200 with empty records."""
        response = client.get("/api/v1/feedback")
        assert response.status_code == 200

    def test_get_all_feedback_returns_summary(self, client: TestClient, sample_feedback: dict):
        """Response must include a sentiment summary section."""
        client.post("/api/v1/feedback", json=sample_feedback)
        response = client.get("/api/v1/feedback")
        data = response.json()
        assert "summary" in data
        assert "records" in data

    def test_get_all_feedback_summary_total_is_correct(
        self, client: TestClient, sample_feedback: dict, negative_feedback: dict
    ):
        """After submitting 2 records, summary total must be 2."""
        client.post("/api/v1/feedback", json=sample_feedback)
        client.post("/api/v1/feedback", json=negative_feedback)
        response = client.get("/api/v1/feedback")
        data = response.json()
        assert data["summary"]["total"] == 2


class TestGetFeedbackById:
    """Tests for GET /api/v1/feedback/{id} (Read One operation)."""

    def test_get_existing_record_returns_200(
        self, client: TestClient, sample_feedback: dict
    ):
        """GET an existing record must return 200."""
        client.post("/api/v1/feedback", json=sample_feedback)
        response = client.get("/api/v1/feedback/1")
        assert response.status_code == 200

    def test_get_existing_record_returns_correct_roll_number(
        self, client: TestClient, sample_feedback: dict
    ):
        """The returned record must match the submitted roll number."""
        client.post("/api/v1/feedback", json=sample_feedback)
        response = client.get("/api/v1/feedback/1")
        data = response.json()
        assert data["roll_number"] == "CS2021001"

    def test_get_nonexistent_record_returns_404(self, client: TestClient):
        """
        GET a record that does not exist must return 404 Not Found.

        This tests our _find_record() helper and HTTPException handling.
        """
        response = client.get("/api/v1/feedback/999")
        assert response.status_code == 404

    def test_404_response_contains_detail_message(self, client: TestClient):
        """The 404 response must include a human-readable detail message."""
        response = client.get("/api/v1/feedback/999")
        data = response.json()
        assert "detail" in data


class TestUpdateFeedback:
    """Tests for PATCH /api/v1/feedback/{id} (Update operation)."""

    def test_update_existing_record_returns_200(
        self, client: TestClient, sample_feedback: dict
    ):
        """PATCH an existing record must return 200 OK."""
        client.post("/api/v1/feedback", json=sample_feedback)
        response = client.patch(
            "/api/v1/feedback/1",
            json={"emotional_feedback": "Sad", "academic_feedback": "Bad"},
        )
        assert response.status_code == 200

    def test_update_recalculates_sentiment(
        self, client: TestClient, sample_feedback: dict
    ):
        """
        Updating emotional and academic feedback must trigger
        sentiment recalculation.

        Originally Happy + Good = Positive.
        After update Sad + Bad = Negative.
        """
        client.post("/api/v1/feedback", json=sample_feedback)
        response = client.patch(
            "/api/v1/feedback/1",
            json={"emotional_feedback": "Sad", "academic_feedback": "Bad"},
        )
        data = response.json()
        assert data["sentiment_label"] == "Negative"

    def test_update_nonexistent_record_returns_404(self, client: TestClient):
        """PATCH on a non-existent ID must return 404."""
        response = client.patch(
            "/api/v1/feedback/999",
            json={"emotional_feedback": "Happy"},
        )
        assert response.status_code == 404


class TestDeleteFeedback:
    """Tests for DELETE /api/v1/feedback/{id} (Delete operation)."""

    def test_delete_existing_record_returns_204(
        self, client: TestClient, sample_feedback: dict
    ):
        """
        DELETE an existing record must return 204 No Content.

        204 means: action successful, nothing to return.
        This is the correct REST standard for DELETE.
        """
        client.post("/api/v1/feedback", json=sample_feedback)
        response = client.delete("/api/v1/feedback/1")
        assert response.status_code == 204

    def test_deleted_record_no_longer_retrievable(
        self, client: TestClient, sample_feedback: dict
    ):
        """After deletion, trying to GET the same record must return 404."""
        client.post("/api/v1/feedback", json=sample_feedback)
        client.delete("/api/v1/feedback/1")
        response = client.get("/api/v1/feedback/1")
        assert response.status_code == 404

    def test_delete_nonexistent_record_returns_404(self, client: TestClient):
        """DELETE on a non-existent ID must return 404."""
        response = client.delete("/api/v1/feedback/999")
        assert response.status_code == 404