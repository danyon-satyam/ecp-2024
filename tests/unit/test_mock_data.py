"""
Unit tests for the mock data generation service.

These tests ensure our Faker + Polyfactory factories generate
data that is always valid according to our Pydantic schemas.

Why test mock data generators?
  If our factory generates invalid data, every test that uses it
  will fail with confusing validation errors. These tests catch
  factory bugs early and keep them separate from API bugs.
"""
import pytest
from app.services.mock_data import (
    generate_student_feedback,
    generate_feedback_dict,
    StudentFeedbackFactory,
)
from app.schemas.student import StudentFeedbackCreate

VALID_GENDERS = {"Male", "Female", "Other"}
VALID_ACADEMIC = {"Excellent", "Good", "Satisfactory", "Bad"}
VALID_EMOTIONAL = {"Happy", "Glad", "Neutral", "Sad", "Angry"}
VALID_SENTIMENTS = {"Positive", "Neutral", "Negative"}


class TestStudentFeedbackFactory:
    """Tests for the Polyfactory-based StudentFeedbackFactory."""

    def test_factory_generates_valid_pydantic_object(self):
        """Factory must produce a valid StudentFeedbackCreate instance."""
        result = StudentFeedbackFactory.build()
        assert isinstance(result, StudentFeedbackCreate)

    def test_factory_gender_is_valid(self):
        """Generated gender must be one of the allowed values."""
        for _ in range(20):
            result = StudentFeedbackFactory.build()
            assert result.gender in VALID_GENDERS

    def test_factory_age_within_range(self):
        """Generated age must be between 17 and 35."""
        for _ in range(20):
            result = StudentFeedbackFactory.build()
            assert 17 <= result.age <= 35

    def test_factory_academic_feedback_is_valid(self):
        """Generated academic feedback must be one of the allowed values."""
        for _ in range(20):
            result = StudentFeedbackFactory.build()
            assert result.academic_feedback in VALID_ACADEMIC

    def test_factory_emotional_feedback_is_valid(self):
        """Generated emotional feedback must be one of the allowed values."""
        for _ in range(20):
            result = StudentFeedbackFactory.build()
            assert result.emotional_feedback in VALID_EMOTIONAL

    def test_factory_attendance_within_range(self):
        """Generated attendance must be between 0 and 100."""
        for _ in range(20):
            result = StudentFeedbackFactory.build()
            assert 0 <= result.attendance_percentage <= 100

    def test_factory_backlogs_non_negative(self):
        """Generated backlogs must be 0 or positive."""
        for _ in range(20):
            result = StudentFeedbackFactory.build()
            assert result.active_backlogs >= 0

    def test_factory_roll_number_is_string(self):
        """Roll number must be a non-empty string."""
        result = StudentFeedbackFactory.build()
        assert isinstance(result.roll_number, str)
        assert len(result.roll_number) > 0


class TestGenerateStudentFeedback:
    """Tests for the generate_student_feedback() helper function."""

    def test_generates_correct_count(self):
        """Function must return exactly the requested number of records."""
        results = generate_student_feedback(10)
        assert len(results) == 10

    def test_generates_351_records(self):
        """Must handle generating 351 records matching our CSV dataset."""
        results = generate_student_feedback(351)
        assert len(results) == 351

    def test_all_records_are_valid_schema(self):
        """Every generated record must be a valid StudentFeedbackCreate."""
        results = generate_student_feedback(50)
        for record in results:
            assert isinstance(record, StudentFeedbackCreate)

    def test_roll_numbers_are_unique(self):
        """
        Roll numbers should have high uniqueness across a batch.

        We check that at least 80% are unique — not 100% because
        random generation can occasionally produce duplicates, and
        that is acceptable for mock data.
        """
        results = generate_student_feedback(100)
        roll_numbers = [r.roll_number for r in results]
        unique_ratio = len(set(roll_numbers)) / len(roll_numbers)
        assert unique_ratio >= 0.80


class TestGenerateFeedbackDict:
    """Tests for the generate_feedback_dict() helper function."""

    def test_returns_list_of_dicts(self):
        """Output must be a list of plain dictionaries."""
        results = generate_feedback_dict(5)
        assert isinstance(results, list)
        assert all(isinstance(r, dict) for r in results)

    def test_dicts_contain_required_keys(self):
        """Each dictionary must contain all required feedback fields."""
        required_keys = {
            "roll_number", "gender", "age", "study_hours_per_day",
            "attendance_percentage", "active_backlogs",
            "academic_feedback", "emotional_feedback",
        }
        results = generate_feedback_dict(5)
        for record in results:
            assert required_keys.issubset(record.keys())