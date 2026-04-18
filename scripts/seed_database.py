"""
Database seeder script.

Populates the database with realistic mock student feedback data
using our Faker + Polyfactory mock data service.

Usage:
    python scripts/seed_database.py              # Seeds 351 records (matching our CSV)
    python scripts/seed_database.py --count 500  # Seeds 500 records
    python scripts/seed_database.py --clear      # Clears existing data first

Why 351 records?
    Our original CSV has 351 student records. We match this count
    so visualisations are comparable between real and mock data.

Why a separate script and not an API endpoint?
    Seeding is a one-time admin operation, not a user-facing feature.
    Scripts are simpler, faster, and safer for bulk database operations.
    They are not exposed to the internet — no security risk.
"""
import sys
import argparse

# Add the project root to Python path so we can import app modules
sys.path.insert(0, ".")

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.student_feedback import Base, StudentFeedback
from app.services.mock_data import generate_student_feedback
from app.services.sentiment import calculate_sentiment


def clear_database(db: Session) -> None:
    """Delete all existing feedback records from the database."""
    count = db.query(StudentFeedback).count()
    db.query(StudentFeedback).delete()
    db.commit()
    print(f"Cleared {count} existing records.")


def seed_database(db: Session, count: int = 351) -> None:
    """
    Seed the database with mock student feedback records.

    Args:
        db: Database session
        count: Number of records to generate and insert
    """
    print(f"Generating {count} realistic student feedback records...")

    feedback_objects = generate_student_feedback(count)

    records = []
    for feedback in feedback_objects:
        sentiment = calculate_sentiment(
            emotional_feedback=feedback.emotional_feedback,
            academic_feedback=feedback.academic_feedback,
        )
        record = StudentFeedback(
            **feedback.model_dump(),
            sentiment_label=sentiment,
        )
        records.append(record)

    # Bulk insert — much faster than inserting one by one
    db.bulk_save_objects(records)
    db.commit()

    print(f"Successfully seeded {count} records.")

    # Print a quick summary
    total = db.query(StudentFeedback).count()
    positive = db.query(StudentFeedback).filter(
        StudentFeedback.sentiment_label == "Positive"
    ).count()
    neutral = db.query(StudentFeedback).filter(
        StudentFeedback.sentiment_label == "Neutral"
    ).count()
    negative = db.query(StudentFeedback).filter(
        StudentFeedback.sentiment_label == "Negative"
    ).count()

    print("\n--- Sentiment Distribution ---")
    print(f"Total records : {total}")
    print(f"Positive      : {positive} ({round(positive/total*100, 1)}%)")
    print(f"Neutral       : {neutral} ({round(neutral/total*100, 1)}%)")
    print(f"Negative      : {negative} ({round(negative/total*100, 1)}%)")
    print("------------------------------\n")


def main() -> None:
    """Parse arguments and run the seeder."""
    parser = argparse.ArgumentParser(
        description="Seed the database with mock student feedback data."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=351,
        help="Number of records to generate (default: 351)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing records before seeding",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.clear:
            clear_database(db)
        seed_database(db, count=args.count)
    finally:
        db.close()


if __name__ == "__main__":
    main()