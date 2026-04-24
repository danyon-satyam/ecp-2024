# Dockerfile
# Student Sentiment Analysis API
#
# This file defines how to build the Docker image for our FastAPI app.
# Every line is an instruction. Docker executes them top to bottom
# and caches each layer — unchanged layers reuse the cache (fast rebuilds).
#
# Build the image:
#   docker build -t sentiment-api .
#
# Run the container:
#   docker run -p 8000:8000 sentiment-api

# ─────────────────────────────────────────────
# Stage 1: Base image
# ─────────────────────────────────────────────
# python:3.11-slim is a minimal Python image — no unnecessary tools.
# 'slim' saves ~400MB compared to the full image.
# We pin the exact version (3.11-slim) so builds are reproducible —
# the same Dockerfile always produces the same image.
FROM python:3.11-slim

# ─────────────────────────────────────────────
# Stage 2: System dependencies
# ─────────────────────────────────────────────
# libpq-dev: required by psycopg2 to connect to PostgreSQL
# gcc: C compiler required to build some Python packages
# --no-install-recommends: skip optional packages to keep image small
# rm -rf /var/lib/apt/lists/*: delete apt cache to reduce image size
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────
# Stage 3: Working directory
# ─────────────────────────────────────────────
# /app is where our code lives inside the container.
# All subsequent commands run from this directory.
WORKDIR /app

# ─────────────────────────────────────────────
# Stage 4: Install Python dependencies
# ─────────────────────────────────────────────
# IMPORTANT: Copy requirements.txt FIRST, before copying the rest of code.
# Why? Docker caches each layer. If requirements.txt hasn't changed,
# Docker reuses the cached pip install layer — saving 2-3 minutes
# on every rebuild. If you copy all code first, any code change
# invalidates the pip cache.
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────
# Stage 5: Copy application code (Strict Selection)
# ─────────────────────────────────────────────
# Instead of everything (.), we only copy specific needed folders and files.
# This is a best practice for security and image size — we avoid copying
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY app/ ./app/
COPY scripts/ ./scripts/

# ─────────────────────────────────────────────
# Stage 6: Create directory for ML model
# ─────────────────────────────────────────────
# The ML model files (.joblib) are excluded from Git but need to exist
# in the container. In production (GCP), they are copied from
# Cloud Storage during deployment. Locally, we mount the volume.
RUN mkdir -p app/ml

# ─────────────────────────────────────────────
# Stage 7: Runtime configuration
# ─────────────────────────────────────────────
# Tell Docker this container listens on port 8000.
# This is documentation only — you still need -p 8000:8000 when running.
EXPOSE 8000

# Environment variables with safe defaults.
# Real secrets (DATABASE_URL, etc.) come from .env or GCP Secret Manager
# at runtime — never hardcoded here.
ENV APP_NAME="Student Sentiment Analysis API"
ENV DEBUG="False"
ENV API_V1_PREFIX="/api/v1"

# ─────────────────────────────────────────────
# Stage 8: Startup command
# ─────────────────────────────────────────────
# CMD is the command that runs when the container starts.
# We use uvicorn directly (not our start_server.py script) because
# in production, the number of workers is controlled by the
# container orchestrator (Cloud Run), not by us.
#
# --host 0.0.0.0: listen on all network interfaces (not just localhost)
# This is required for the container to be accessible from outside.
# 127.0.0.1 would make it unreachable from the host machine.
# Copy the startup script and make it executable
COPY scripts/gcp_startup.sh /app/scripts/gcp_startup.sh
RUN chmod +x /app/scripts/gcp_startup.sh

# For local Docker: use uvicorn directly
# For GCP: override this CMD with the startup script
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]