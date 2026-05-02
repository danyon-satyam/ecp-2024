# GCP Deployment Guide

**Project:** Student Sentiment Analysis API
**Author:** Danyon Satyam
**Mentor:** Pramit Dash
**Target:** Google Cloud Platform — Cloud Run

---

## Prerequisites

Before deploying, ensure you have:

- [ ] Google Cloud account created
- [ ] Google Cloud CLI (`gcloud`) installed
- [ ] Docker Desktop running
- [ ] All tests passing (`pytest -v`)
- [ ] ML model trained (`python scripts/train_model.py`)

---

## GCP Services Used

| Service           | Purpose                  | Why                                      |
| ----------------- | ------------------------ | ---------------------------------------- |
| Cloud Run         | Runs FastAPI container   | Serverless, auto-scales, pay per request |
| Cloud SQL         | Managed PostgreSQL       | Automatic backups, no server management  |
| Cloud Storage     | ML model files           | Large binary files outside the image     |
| Secret Manager    | DATABASE_URL and secrets | Never hardcode secrets                   |
| Artifact Registry | Docker image storage     | Cloud Run pulls images from here         |

---

## Step 1 — Install Google Cloud CLI

Download from: https://cloud.google.com/sdk/docs/install

After installation, authenticate:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

## Step 2 — Create GCP Project

```bash
# Create project
gcloud projects create sentiment-api-prod --name="Sentiment API"

# Set as default
gcloud config set project sentiment-api-prod

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com
```

---

## Step 3 — Create Cloud SQL Instance

```bash
# Create PostgreSQL instance (takes 5-10 minutes)
gcloud sql instances create sentiment-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-south1

# Create database
gcloud sql databases create sentiment_db \
  --instance=sentiment-db

# Set postgres user password
gcloud sql users set-password postgres \
  --instance=sentiment-db \
  --password=YOUR_SECURE_PASSWORD
```

---

## Step 4 — Create Cloud Storage Bucket for ML Model

```bash
# Create bucket in India region (closest to our target universities)
gsutil mb -l asia-south1 gs://sentiment-api-models

# Upload trained ML model files
gsutil cp app/ml/sentiment_model.joblib gs://sentiment-api-models/
gsutil cp app/ml/label_encoders.joblib gs://sentiment-api-models/
```

---

## Step 5 — Store Secrets in Secret Manager

```bash
# Store database URL as a secret
echo -n "postgresql://postgres:YOUR_PASSWORD@/sentiment_db?host=/cloudsql/PROJECT:REGION:INSTANCE" \
  | gcloud secrets create DATABASE_URL --data-file=-

# Verify secret exists
gcloud secrets list
```

---

## Step 6 — Create Artifact Registry Repository

```bash
# Create Docker repository
gcloud artifacts repositories create sentiment-api \
  --repository-format=docker \
  --location=asia-south1

# Configure Docker to authenticate with GCP
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

---

## Step 7 — Build and Push Docker Image

```bash
# Tag and build the image for GCP
docker build -t asia-south1-docker.pkg.dev/sentiment-api-prod/sentiment-api/app:latest .

# Push to Artifact Registry
docker push asia-south1-docker.pkg.dev/sentiment-api-prod/sentiment-api/app:latest
```

---

## Step 8 — Deploy to Cloud Run

```bash
gcloud run deploy sentiment-api \
  --image=asia-south1-docker.pkg.dev/sentiment-api-prod/sentiment-api/app:latest \
  --platform=managed \
  --region=asia-south1 \
  --allow-unauthenticated \
  --add-cloudsql-instances=sentiment-api-prod:asia-south1:sentiment-db \
  --set-secrets=DATABASE_URL=DATABASE_URL:latest \
  --set-env-vars="APP_NAME=Student Sentiment Analysis API,DEBUG=False" \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --port=8000
```

---

## Step 9 — Run Migrations on Cloud SQL

```bash
# Connect to Cloud SQL and run migrations
gcloud run jobs create run-migrations \
  --image=asia-south1-docker.pkg.dev/sentiment-api-prod/sentiment-api/app:latest \
  --region=asia-south1 \
  --add-cloudsql-instances=sentiment-api-prod:asia-south1:sentiment-db \
  --set-secrets=DATABASE_URL=DATABASE_URL:latest \
  --command="alembic" \
  --args="upgrade,head"

gcloud run jobs execute run-migrations --region=asia-south1
```

---

## Estimated Monthly Cost (Minimal Usage)

| Service         | Tier          | Estimated Cost             |
| --------------- | ------------- | -------------------------- |
| Cloud Run       | 0-5 instances | ~$0-5 (free tier generous) |
| Cloud SQL       | db-f1-micro   | ~$7-10/month               |
| Cloud Storage   | < 1GB         | ~$0.02/month               |
| Secret Manager  | < 10 secrets  | Free tier                  |
| **Total** |               | **~$7-15/month**     |

---

## Environment Differences

| Setting  | Local              | Docker Local       | GCP Production    |
| -------- | ------------------ | ------------------ | ----------------- |
| Database | Local PostgreSQL   | Docker PostgreSQL  | Cloud SQL         |
| ML Model | `app/ml/` folder | Volume mount       | Cloud Storage     |
| Secrets  | `.env` file      | docker-compose env | Secret Manager    |
| Workers  | 4 (Windows: 1)     | 1                  | Cloud Run manages |
| SSL      | No                 | No                 | Yes (automatic)   |
