# ADR-008: Docker Containerisation Strategy

**Date:** 2026-04-14
**Status:** Accepted
**Author:** Danyon Satyam
**Reviewed by:** Pramit Dash

---

## Context

The application needs to run consistently across three environments:
local development (Windows), CI/CD (Ubuntu on GitHub Actions), and
production (GCP Cloud Run on Linux). Environment differences cause
"works on my machine" failures that are hard to diagnose.

Additionally, GCP Cloud Run requires a containerised application —
it cannot run raw Python code directly.

---

## Decision

We containerise the application using **Docker** with a single-stage
`python:3.11-slim` base image and orchestrate local development with
**docker-compose**.

---

## Reasons

**Environment consistency:** The same Docker image runs on Windows,
Ubuntu CI, and GCP Linux. Dependency versions are locked. No more
"it works on my machine" failures.

**GCP Cloud Run requirement:** Cloud Run is a container execution
platform — it requires a Docker image. This is not optional.

**Isolation:** The container has its own filesystem and dependencies.
It cannot be affected by other software on the host machine.

**`python:3.11-slim` over `python:3.11`:** The slim variant is ~400MB
smaller. Smaller images deploy faster to GCP and cost less storage.

**docker-compose for local development:** Runs the full stack
(API + PostgreSQL + migrations) with one command. New developers
can start the project without installing PostgreSQL locally.

---

## Image Layer Strategy

We copy `requirements.txt` before copying the rest of the code.
This exploits Docker's layer caching — if dependencies haven't
changed, Docker reuses the cached pip install layer, reducing
rebuild time from ~3 minutes to ~10 seconds.

---

## ML Model Handling

The trained `.joblib` model files are excluded from the Docker image
(too large for version control and images). They are:

- Local development: mounted as a Docker volume from `./app/ml`
- Production (GCP): copied from Cloud Storage at startup

---

## Consequences

- Docker Desktop must be installed for local development
- `docker-compose up` replaces `uvicorn app.main:app --reload`
  for full-stack local development
- ML model files must be trained before running the container
- CI/CD pipeline builds and pushes the image to GCP Artifact Registry
