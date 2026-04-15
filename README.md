
# Student Sentiment Analysis API

[![CI Pipeline](https://github.com/danyon-satyam/ecp-2024/actions/workflows/ci.yml/badge.svg)](https://github.com/danyon-satyam/ecp-2024/actions/workflows/ci.yml)

A production-grade REST API for analysing student sentiment at universities.
Built with FastAPI, Python, and Machine Learning.

## Project Overview

This API allows universities to collect student feedback at scale and
automatically analyse the emotional and academic sentiment using ML models.
It is designed to handle hundreds of concurrent users and is built following
enterprise software engineering practices.

## Tech Stack

| Layer           | Technology           | Purpose                             |
| --------------- | -------------------- | ----------------------------------- |
| Web Framework   | FastAPI              | REST API and Swagger UI             |
| Server          | Uvicorn              | ASGI server for async handling      |
| Data Validation | Pydantic v2          | Schema validation and serialisation |
| ML / Sentiment  | VADER + Scikit-learn | Sentiment analysis                  |
| Testing         | Pytest + TestClient  | TDD and automated testing           |
| CI/CD           | GitHub Actions       | Automated test pipeline             |
| Deployment      | GCP (planned)        | Cloud hosting at scale              |

## Project Structure

ecp-2024/
├── app/
│   ├── api/v1/endpoints/   ← API route handlers
│   ├── core/               ← Config and settings
│   ├── models/             ← Database models
│   ├── schemas/            ← Pydantic request/response schemas
│   └── services/           ← Business logic (sentiment analysis)
├── tests/
│   ├── unit/               ← Unit tests for individual functions
│   └── integration/        ← End-to-end API tests
├── docs/adrs/              ← Architecture Decision Records
└── notebooks/              ← Original ML research notebook

## Local Setup

```bash
# Clone the repository
git clone https://github.com/danyon-satyam/ecp-2024.git
cd ecp-2024

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the API server
uvicorn app.main:app --reload
```

The API will be live at `http://127.0.0.1:8000`
Swagger UI available at `http://127.0.0.1:8000/docs`

## Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run with coverage report
pytest -v
```

## API Endpoints

| Method | Endpoint                  | Description                   |
| ------ | ------------------------- | ----------------------------- |
| GET    | `/health`               | Check API is running          |
| POST   | `/api/v1/feedback`      | Submit student feedback       |
| GET    | `/api/v1/feedback`      | Get all feedback with summary |
| GET    | `/api/v1/feedback/{id}` | Get one feedback record       |
| PATCH  | `/api/v1/feedback/{id}` | Update a feedback record      |
| DELETE | `/api/v1/feedback/{id}` | Delete a feedback record      |

## Developer

- **Project by:** Danyon Satyam
- **Mentor / Client:** Pramit Dash
- **Collaborator:** Samarth
