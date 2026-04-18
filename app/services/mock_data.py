"""
Mock data generation using Faker and Polyfactory.

Why mock data?
  Real university data has privacy concerns — you cannot use actual
  student records for development and testing. Faker generates
  realistic-looking data that behaves like real data without
  exposing anyone's personal information.

Polyfactory integrates with Pydantic schemas to automatically generate
valid fake objects. It respects all your validation rules — so generated
data will always pass your schema validators.

Use cases:
  - Populate the development database for building visualisations
  - Generate large datasets for load testing (100s of concurrent users)
  - Demo the app to Pramit with realistic-looking data
  - Reproduce edge cases in testing (all Negative sentiment, all backlogs)
"""
import random
from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.student import StudentFeedbackCreate
from app.services.sentiment import calculate_sentiment

# Initialise Faker with Indian locale for realistic Indian university data
fake = Faker("en_IN")

# Valid options matching our Pydantic validators
GENDERS = ["Male", "Female", "Other"]
ACADEMIC_FEEDBACK_OPTIONS = ["Excellent", "Good", "Satisfactory", "Bad"]
EMOTIONAL_FEEDBACK_OPTIONS = ["Happy", "Glad", "Neutral", "Sad", "Angry"]

# Weighted distributions — matching realistic university patterns
# Most students are doing okay, some struggling, some excelling
ACADEMIC_WEIGHTS = [0.15, 0.40, 0.30, 0.15]   # Excellent, Good, Satisfactory, Bad
EMOTIONAL_WEIGHTS = [0.25, 0.20, 0.30, 0.15, 0.10]  # Happy, Glad, Neutral, Sad, Angry


class StudentFeedbackFactory(ModelFactory):
    """
    Polyfactory factory for generating StudentFeedbackCreate objects.

    ModelFactory automatically generates valid data for all fields
    by inspecting the Pydantic schema. We override specific fields
    to use more realistic distributions via Faker.

    Why ModelFactory over plain Faker?
      ModelFactory respects Pydantic validators automatically.
      If we add a new field with constraints to the schema,
      the factory adapts without code changes.
    """

    __model__ = StudentFeedbackCreate

    @classmethod
    def roll_number(cls) -> str:
        """Generate a realistic university roll number."""
        dept = random.choice(["CS", "EC", "ME", "CE", "IT", "EE"])
        year = random.randint(2020, 2024)
        number = random.randint(1, 120)
        return f"{dept}{year}{number:03d}"

    @classmethod
    def gender(cls) -> str:
        """Generate gender with realistic distribution."""
        return random.choices(GENDERS, weights=[0.55, 0.43, 0.02])[0]

    @classmethod
    def age(cls) -> int:
        """Generate realistic student age (17-25 most common)."""
        return random.choices(
            range(17, 36),
            weights=[1, 3, 5, 6, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        )[0]

    @classmethod
    def study_hours_per_day(cls) -> int:
        """Generate study hours — most students study 4-8 hours."""
        return random.choices(
            range(1, 25),
            weights=[1, 2, 4, 6, 8, 8, 6, 5, 4, 3, 2, 2, 1, 1, 1,
                     1, 1, 1, 1, 1, 1, 1, 1, 1],
        )[0]

    @classmethod
    def attendance_percentage(cls) -> int:
        """Generate attendance — most students have 60-90% attendance."""
        return random.randint(30, 100)

    @classmethod
    def active_backlogs(cls) -> int:
        """Generate backlogs — most students have 0, some have 1-3."""
        return random.choices([0, 1, 2, 3, 4, 5], weights=[60, 20, 10, 5, 3, 2])[0]

    @classmethod
    def academic_feedback(cls) -> str:
        """Generate academic feedback with realistic weighted distribution."""
        return random.choices(ACADEMIC_FEEDBACK_OPTIONS, weights=ACADEMIC_WEIGHTS)[0]

    @classmethod
    def emotional_feedback(cls) -> str:
        """Generate emotional feedback with realistic weighted distribution."""
        return random.choices(EMOTIONAL_FEEDBACK_OPTIONS, weights=EMOTIONAL_WEIGHTS)[0]


def generate_student_feedback(count: int = 1) -> list[StudentFeedbackCreate]:
    """
    Generate a list of realistic student feedback objects.

    Args:
        count: Number of student feedback records to generate

    Returns:
        List of valid StudentFeedbackCreate Pydantic objects
    """
    return StudentFeedbackFactory.batch(count)


def generate_feedback_dict(count: int = 1) -> list[dict]:
    """
    Generate student feedback as plain dictionaries.

    Useful for seeding the database directly via the repository.

    Args:
        count: Number of records to generate

    Returns:
        List of dictionaries with all feedback fields
    """
    records = generate_student_feedback(count)
    return [record.model_dump() for record in records]