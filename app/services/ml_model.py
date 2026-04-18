"""
ML Model Service — loads and serves the trained CatBoost model.

This service is the bridge between the trained ML artifact on disk
and the FastAPI endpoints that need predictions.

Design decisions:
  - Model is loaded ONCE at module import time (not per request)
    Loading a model takes ~100ms. If we loaded it per request, the API
    would be 100x slower under load. Loading once means zero overhead
    per prediction.

  - Fallback to rule-based scoring if model file is missing
    This means the API still works during development before training,
    and during CI where we do not load the model file.

  - Singleton pattern: one global model instance shared across all requests
    Thread-safe for read operations (predictions never modify the model).
"""
import joblib
import numpy as np
from pathlib import Path
from typing import Optional

MODEL_PATH = Path("app/ml/sentiment_model.joblib")
ENCODER_PATH = Path("app/ml/label_encoders.joblib")


class SentimentMLService:
    """
    Service that wraps the trained CatBoost model for prediction.

    Provides a clean interface so the rest of the app never needs
    to know whether predictions come from ML or rule-based fallback.
    """

    def __init__(self) -> None:
        """Load the model and encoders from disk on initialisation."""
        self.model = None
        self.encoders: dict = {}
        self.is_ml_ready: bool = False
        self._load_model()

    def _load_model(self) -> None:
        """
        Load the trained model and encoders from disk.

        Silently falls back to rule-based mode if files are missing.
        This allows the API to run in development without trained artifacts.
        """
        if MODEL_PATH.exists() and ENCODER_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
                self.encoders = joblib.load(ENCODER_PATH)
                self.is_ml_ready = True
                print(f"ML model loaded successfully from {MODEL_PATH}")
            except Exception as e:
                print(f"Warning: Could not load ML model: {e}. Using rule-based fallback.")
                self.is_ml_ready = False
        else:
            print(
                "ML model files not found. "
                "Run 'python scripts/train_model.py' to train. "
                "Using rule-based fallback."
            )

    def predict(self, emotional_feedback: str, academic_feedback: str) -> str:
        """
        Predict sentiment for a student feedback record.

        Uses the trained CatBoost model if available,
        falls back to weighted rule-based scoring otherwise.

        Args:
            emotional_feedback: Student's emotional state (e.g. 'Happy')
            academic_feedback: Student's academic satisfaction (e.g. 'Good')

        Returns:
            Sentiment label: 'Positive', 'Neutral', or 'Negative'
        """
        if self.is_ml_ready:
            return self._ml_predict(emotional_feedback, academic_feedback)
        return self._rule_based_predict(emotional_feedback, academic_feedback)

    def _ml_predict(self, emotional_feedback: str, academic_feedback: str) -> str:
        """
        Use the trained CatBoost model for prediction.

        Encodes the input features using the saved LabelEncoders
        before passing to the model.
        """
        try:
            # Encode emotional feedback
            emotional_enc = self.encoders.get("emotional_feedback")
            academic_enc = self.encoders.get("academic_feedback")

            if emotional_enc and academic_enc:
                # Handle unseen labels gracefully
                emotional_classes = list(emotional_enc.classes_)
                academic_classes = list(academic_enc.classes_)

                emotional_val = (
                    emotional_enc.transform([emotional_feedback])[0]
                    if emotional_feedback in emotional_classes
                    else 0
                )
                academic_val = (
                    academic_enc.transform([academic_feedback])[0]
                    if academic_feedback in academic_classes
                    else 0
                )
            else:
                emotional_val = 0
                academic_val = 0

            features = np.array([[emotional_val, academic_val]])
            prediction = self.model.predict(features)

            # CatBoost returns nested array — extract the label
            if isinstance(prediction, np.ndarray):
                label = prediction.flatten()[0]
            else:
                label = prediction

            return str(label)

        except Exception as e:
            print(f"ML prediction error: {e}. Falling back to rule-based.")
            return self._rule_based_predict(emotional_feedback, academic_feedback)

    def _rule_based_predict(
        self, emotional_feedback: str, academic_feedback: str
    ) -> str:
        """
        Rule-based fallback sentiment prediction.

        Uses the weighted scoring methodology from the research notebook.
        Always available — no model file required.
        """
        emotional_map = {
            "Happy": 1, "Glad": 1, "Neutral": 0, "Sad": -1, "Angry": -1
        }
        academic_map = {
            "Excellent": 1, "Good": 1, "Satisfactory": 0, "Bad": -1
        }

        emotional_score = emotional_map.get(emotional_feedback, 0)
        academic_score = academic_map.get(academic_feedback, 0)

        weighted = 0.7 * emotional_score + 0.3 * academic_score

        if weighted > 0:
            return "Positive"
        elif weighted < 0:
            return "Negative"
        return "Neutral"

    def get_model_info(self) -> dict:
        """
        Return metadata about the current prediction mode.

        Used by the /health and /model-info endpoints so clients
        know whether ML or rule-based predictions are active.
        """
        return {
            "mode": "ml_model" if self.is_ml_ready else "rule_based_fallback",
            "model_type": "CatBoostClassifier" if self.is_ml_ready else "WeightedRuleEngine",
            "model_path": str(MODEL_PATH) if self.is_ml_ready else None,
            "is_ready": self.is_ml_ready,
        }


# Global singleton instance — loaded once when the module is first imported
# All API requests share this one instance (thread-safe for predictions)
sentiment_ml_service = SentimentMLService()