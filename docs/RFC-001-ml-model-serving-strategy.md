# RFC-001: ML Model Serving Strategy

**RFC Number:** 001
**Title:** Strategy for Serving the CatBoost Sentiment Model in FastAPI
**Author:** Danyon Satyam
**Date:** April 2026
**Status:** Accepted
**Reviewers:** Pramit Dash

---

## Summary

This RFC proposes loading the trained CatBoost model once at
application startup as a global singleton, with automatic fallback
to rule-based scoring when the model file is unavailable.

---

## Motivation

The FastAPI application needs to serve ML predictions for every
POST /feedback request. The key engineering question is: when and
how should the model be loaded?

Three options were considered:

**Option A — Load model per request**
Load from disk every time a prediction is needed.

- Problem: ~100ms disk read per request. At 100 concurrent users
  this adds 100ms latency to every request. Unacceptable.

**Option B — Load model at startup (singleton)**
Load once when the application starts. All requests share one instance.

- Benefit: Zero per-request overhead after startup.
- Benefit: Thread-safe for read-only predictions.
- Consideration: Startup takes slightly longer (~200ms more).
- This is the standard MLOps serving pattern.

**Option C — Model microservice (separate API)**
Run the ML model as a separate FastAPI service.

- Overkill for our scale. Adds network latency between services.
- Appropriate for very large models (GPT-scale) — not CatBoost.

---

## Proposal

Adopt **Option B** — singleton model loaded at startup.

Implementation:

- `SentimentMLService` class loads model in `__init__`
- Module-level instance: `sentiment_ml_service = SentimentMLService()`
- `calculate_sentiment()` delegates to this singleton
- If model files are missing: automatic fallback to rule-based scoring
- `/health` endpoint exposes model readiness status

---

## Fallback Strategy

The rule-based fallback ensures the API is never "broken" by missing
model files. This matters for:

- CI environment (no model file present)
- Development before first training run
- Recovery if model file is corrupted

The fallback uses the same weighted scoring methodology documented
in the research notebook, so results are meaningful even without ML.

---

## Consequences

- `python scripts/train_model.py` must be run before production deployment
- Model files (.joblib) are NOT committed to Git (too large, binary)
- In production (GCP), model files will be loaded from Cloud Storage
- `/health` endpoint allows monitoring systems to detect model failures

---

## Decision

Accepted. Implementation completed in `app/services/ml_model.py`.
