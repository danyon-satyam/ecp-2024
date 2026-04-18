"""
ML Model Training Script.

Trains the CatBoost sentiment classifier using the real student
data from our university CSV dataset and saves the trained model
to disk so the FastAPI service can load it at startup.

Why a separate training script and not inside the API?
  Training is a one-time (or periodic) operation — not a per-request
  operation. Training inside the API would slow startup massively.
  Instead: train once → save model file → API loads the saved file.

This is the standard MLOps pattern:
  Training pipeline (offline) → Model artifact → Serving API (online)

Usage:
    python scripts/train_model.py
"""
import sys
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    mean_squared_error,
)
from catboost import CatBoostClassifier

# Add project root to path
sys.path.insert(0, ".")

# Paths
DATA_PATH = Path("notebooks/Student_Information_Data.csv")
MODEL_DIR = Path("app/ml")
MODEL_PATH = MODEL_DIR / "sentiment_model.joblib"
ENCODER_PATH = MODEL_DIR / "label_encoders.joblib"

# Create model directory
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def load_and_clean_data(path: Path) -> pd.DataFrame:
    """
    Load and clean the student feedback CSV dataset.

    Applies the same cleaning steps as the research notebook:
    rename columns, drop unnecessary columns, handle missing values,
    remove duplicates, and strip whitespace from string columns.

    Args:
        path: Path to the CSV file

    Returns:
        Cleaned pandas DataFrame
    """
    print(f"Loading data from {path}...")
    df = pd.read_csv(path)

    # Rename columns to match our API schema
    column_map = {
        "Study Time (Per hours in a Day, including Classes)": "study_hours_per_day",
        "1st Semester CGPA": "cgpa_1st",
        "2nd Semester CGPA ": "cgpa_2nd",
        "3rd Semester CGPA ": "cgpa_3rd",
        "4th Semester CGPA": "cgpa_4th",
        "5th Semester CGPA (If you are in 4th Sem, Expected CGPA)": "cgpa_5th",
        "Attendance (Previous Semester)": "attendance_percentage",
        "Active Backlogs (E.g. 0, 1, 2, 3)": "active_backlogs",
        "Extra Curricular Activities ": "extra_curricular",
        "Feedback (About satisfaction of academic studies at our University)": "academic_feedback",
        "Emotional Feedback  (According to CGPA, Attendance, & Study Hours)": "emotional_feedback",
    }
    df = df.rename(columns=column_map)

    # Drop columns not needed for sentiment prediction
    df = df.drop(columns=["Timestamp", "Roll No.", "Address "], errors="ignore")

    # Handle CGPA columns — strip whitespace and convert to numeric
    cgpa_cols = ["cgpa_1st", "cgpa_2nd", "cgpa_3rd", "cgpa_4th", "cgpa_5th"]
    for col in cgpa_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.replace(",", ".")
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    # Fill missing numeric values with median
    num_cols = df.select_dtypes(include="number").columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    # Fill missing categorical values with mode
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Remove duplicates
    df = df.drop_duplicates()
    df = df.dropna()

    print(f"Cleaned dataset: {len(df)} records, {df.shape[1]} columns")
    return df


def engineer_sentiment_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the sentiment target column using the weighted scoring
    methodology from the research notebook.

    Emotional feedback carries 70% weight, academic feedback 30%.
    This matches ADR-003's documented domain logic.

    Args:
        df: Cleaned DataFrame

    Returns:
        DataFrame with added 'sentiment' target column
    """
    emotional_map = {
        "Happy": 1, "Glad": 1, "Neutral": 0, "Sad": -1, "Angry": -1
    }
    academic_map = {
        "Excellent": 1, "Good": 1, "Satisfactory": 0, "Bad": -1
    }

    emotional_scores = df["emotional_feedback"].map(emotional_map).fillna(0)
    academic_scores = df["academic_feedback"].map(academic_map).fillna(0)

    weighted = 0.7 * emotional_scores + 0.3 * academic_scores

    df["sentiment"] = weighted.apply(
        lambda s: "Positive" if s > 0 else ("Negative" if s < 0 else "Neutral")
    )
    return df


def encode_features(df: pd.DataFrame) -> tuple:
    """
    Encode categorical features using LabelEncoder.

    Saves encoders to disk so the API can use them to encode
    incoming request data before passing it to the model.

    Args:
        df: DataFrame with raw categorical columns

    Returns:
        Tuple of (encoded DataFrame, dict of fitted encoders)
    """
    encoders = {}
    categorical_cols = ["Gender", "academic_feedback",
                        "emotional_feedback", "extra_curricular"]

    for col in categorical_cols:
        if col in df.columns:
            enc = LabelEncoder()
            df[col] = enc.fit_transform(df[col].astype(str))
            encoders[col] = enc
            print(f"Encoded '{col}': {list(enc.classes_)}")

    return df, encoders


def train_and_evaluate(df: pd.DataFrame) -> tuple:
    """
    Train CatBoost classifier and evaluate its performance.

    Uses emotional_feedback and academic_feedback as features —
    the same two features identified as most predictive in the notebook.

    Args:
        df: Preprocessed DataFrame with encoded features

    Returns:
        Tuple of (trained model, accuracy score)
    """
    # Features and target — matching the notebook's best configuration
    X = df[["emotional_feedback", "academic_feedback"]]
    y = df["sentiment"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nTraining set: {len(X_train)} records")
    print(f"Test set    : {len(X_test)} records")

    # CatBoost — best performer from notebook (MSE ~2.81e-07)
    model = CatBoostClassifier(
        iterations=200,
        learning_rate=0.1,
        depth=6,
        loss_function="MultiClass",
        eval_metric="Accuracy",
        random_seed=42,
        verbose=False,
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    # CatBoost returns 2D array for predict — flatten to 1D
    if hasattr(y_pred, "flatten"):
        y_pred = y_pred.flatten()

    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    return model, accuracy


def save_artifacts(model, encoders: dict) -> None:
    """
    Save the trained model and encoders to disk.

    Uses joblib for serialisation — the standard for scikit-learn
    compatible models. joblib is more efficient than pickle for
    large numpy arrays.

    Args:
        model: Trained CatBoost model
        encoders: Dictionary of fitted LabelEncoders
    """
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODER_PATH)
    print(f"\nModel saved to   : {MODEL_PATH}")
    print(f"Encoders saved to: {ENCODER_PATH}")


def main() -> None:
    """Run the full training pipeline."""
    print("=" * 50)
    print("  Student Sentiment Model Training Pipeline")
    print("=" * 50)

    df = load_and_clean_data(DATA_PATH)
    df = engineer_sentiment_target(df)
    df, encoders = encode_features(df)
    model, accuracy = train_and_evaluate(df)
    save_artifacts(model, encoders)

    print("\nTraining complete!")
    print(f"Model ready for serving. Accuracy: {accuracy*100:.2f}%")


if __name__ == "__main__":
    main()