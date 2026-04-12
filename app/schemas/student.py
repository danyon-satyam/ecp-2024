"""
Student Pydantic schemas.

Schemas define the shape of data that comes IN to the API (requests)
and goes OUT of the API (responses). Pydantic validates all data automatically.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class StudentFeedbackCreate(BaseModel):
    """Schema for submitting new student feedback."""

    roll_number: str = Field(..., description="Student roll number", example="CS2021001")
    gender: str = Field(..., description="Student gender", example="Male")
    age: int = Field(..., ge=17, le=35, description="Student age between 17 and 35")
    study_hours_per_day: int = Field(..., ge=1, le=24, description="Daily study hours")
    attendance_percentage: int = Field(..., ge=0, le=100, description="Attendance percentage")
    active_backlogs: int = Field(..., ge=0, description="Number of active backlogs")
    academic_feedback: str = Field(
        ...,
        description="Feedback about academic satisfaction",
        example="Good"
    )
    emotional_feedback: str = Field(
        ...,
        description="Emotional state based on performance",
        example="Happy"
    )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Ensure gender is one of the accepted values."""
        allowed = {"Male", "Female", "Other"}
        if v not in allowed:
            raise ValueError(f"Gender must be one of: {allowed}")
        return v

    @field_validator("academic_feedback")
    @classmethod
    def validate_academic_feedback(cls, v: str) -> str:
        """Ensure academic feedback is a valid category."""
        allowed = {"Excellent", "Good", "Satisfactory", "Bad"}
        if v not in allowed:
            raise ValueError(f"Academic feedback must be one of: {allowed}")
        return v

    @field_validator("emotional_feedback")
    @classmethod
    def validate_emotional_feedback(cls, v: str) -> str:
        """Ensure emotional feedback is a valid category."""
        allowed = {"Happy", "Glad", "Neutral", "Sad", "Angry"}
        if v not in allowed:
            raise ValueError(f"Emotional feedback must be one of: {allowed}")
        return v


class StudentFeedbackResponse(BaseModel):
    """Schema for the API response after submitting feedback."""

    id: int = Field(..., description="Auto-generated record ID")
    roll_number: str
    academic_feedback: str
    emotional_feedback: str
    sentiment_label: str = Field(..., description="Predicted sentiment: Positive, Neutral, or Negative")
    message: str = Field(..., description="Confirmation message")