#!/bin/bash
# scripts/gcp_startup.sh
#
# Startup script for GCP Cloud Run deployment.
# This runs BEFORE the API starts.
#
# Steps:
#   1. Download ML model files from Cloud Storage
#   2. Run Alembic database migrations
#   3. Start the Uvicorn server
#
# Environment variables required (set in Cloud Run):
#   MODEL_BUCKET: GCS bucket name (e.g. sentiment-api-models)
#   DATABASE_URL: PostgreSQL connection string from Secret Manager

set -e  # Exit immediately if any command fails

echo "=== GCP Startup Script ==="

# Step 1: Download ML model files from Cloud Storage
echo "Downloading ML model from Cloud Storage..."
mkdir -p app/ml

if [ -n "$MODEL_BUCKET" ]; then
    gsutil cp gs://$MODEL_BUCKET/sentiment_model.joblib app/ml/ || \
        echo "Warning: Could not download model. Using rule-based fallback."
    gsutil cp gs://$MODEL_BUCKET/label_encoders.joblib app/ml/ || \
        echo "Warning: Could not download encoders. Using rule-based fallback."
    echo "ML model downloaded successfully."
else
    echo "MODEL_BUCKET not set. Using rule-based sentiment fallback."
fi

# Step 2: Run Alembic migrations
echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete."

# Step 3: Start the API server
echo "Starting Uvicorn server..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --log-level info