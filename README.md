# Student Sentiment Analysis API

[![CI](https://github.com/danyon-satyam/ecp-2024/actions/workflows/ci.yml/badge.svg)](https://github.com/danyon-satyam/ecp-2024/actions)
[![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)](https://github.com/danyon-satyam/ecp-2024)
[![Deployment](https://img.shields.io/badge/deployment-live-success)](https://sentiment-api-vpmz.onrender.com/docs)

**🚀 Live Production API:** [https://sentiment-api-vpmz.onrender.com/docs](https://sentiment-api-vpmz.onrender.com/docs)

A production-grade REST API for analyzing university student sentiment through academic and emotional feedback. Built with FastAPI, PostgreSQL, CatBoost ML, containerized with Docker, and deployed on Render.com.

**Status:** ✅ Live in Production | **Region:** EU Central (Frankfurt) | **Records:** 500+ | **Uptime:** 99.9%

---

## 🎯 Quick Links

- **Live API:** [https://sentiment-api-vpmz.onrender.com/docs](https://sentiment-api-vpmz.onrender.com/docs)
- **Health Check:** [https://sentiment-api-vpmz.onrender.com/health](https://sentiment-api-vpmz.onrender.com/health)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Performance:** [docs/PERFORMANCE.md](docs/PERFORMANCE.md)
- **Monitoring:** [docs/MONITORING.md](docs/MONITORING.md)
- **Deployment:** [docs/RENDER_DEPLOYMENT.md](docs/RENDER_DEPLOYMENT.md)

---

## ✨ Key Features

- ✅ **RESTful API** with FastAPI (OpenAPI/Swagger docs)
- ✅ **ML-Powered Sentiment Analysis** (CatBoost model)
- ✅ **PostgreSQL Database** (500+ seeded records)
- ✅ **6 Visualization Endpoints** (Seaborn/Matplotlib charts)
- ✅ **Comprehensive Analytics** (trends, at-risk students, sentiment distribution)
- ✅ **93% Test Coverage** (unit + integration + load tests)
- ✅ **CI/CD Pipeline** (GitHub Actions, auto-deploy from main)
- ✅ **Docker Containerized** (cloud-agnostic deployment)
- ✅ **Production Deployment** (Render.com, auto-scaling)

---

## 🚀 Performance Metrics

**Production (Render Free Tier):**

- **Throughput:** ~12 RPS sustained
- **Latency:** 280ms average (CRUD), 7s (charts)
- **Error Rate:** <1%
- **Uptime:** 99.9%

See [docs/PERFORMANCE.md](docs/PERFORMANCE.md) for detailed benchmarks.

---

## 📊 Example Endpoints

```bash
# Health Check
GET https://sentiment-api-vpmz.onrender.com/health

# Analytics Summary
GET https://sentiment-api-vpmz.onrender.com/api/v1/analytics/summary

# Sentiment Bar Chart (PNG)
GET https://sentiment-api-vpmz.onrender.com/api/v1/visualisations/sentiment-bar

# Submit Feedback
POST https://sentiment-api-vpmz.onrender.com/api/v1/feedback
{
  "roll_number": "CS2024001",
  "gender": "Male",
  "age": 20,
  "academic_feedback": "Good",
  "emotional_feedback": "Happy"
}
```

## Project Overview

This API allows universities to collect student feedback at scale and
automatically analyse the emotional and academic sentiment using ML models.
It is designed to handle hundreds of concurrent users and is built following
enterprise software engineering practices.

---

## 🏗️ Tech Stack

| Layer           | Technology           | Purpose                             |
| --------------- | -------------------- | ----------------------------------- |
| Web Framework   | FastAPI              | REST API and Swagger UI             |
| Server          | Uvicorn              | ASGI server for async handling      |
| Data Validation | Pydantic v2          | Schema validation and serialisation |
| ML / Sentiment  | VADER + Scikit-learn | Sentiment analysis                  |
| Testing         | Pytest + TestClient  | TDD and automated testing           |
| CI/CD           | GitHub Actions       | Automated test pipeline             |
| Deployment      | GCP (planned)        | Cloud hosting at scale              |

---

## 📁 Project Structure

ecp-2024/
├── app/
│   ├── api/v1/endpoints/     # API route handlers
│   ├── core/                 # Config, database, exceptions
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic request/response models
│   ├── services/             # Business logic, ML, analytics
│   └── main.py               # FastAPI application factory
├── tests/
│   ├── unit/                 # Unit tests (mocks, services)
│   ├── integration/          # API integration tests
│   ├── load/                 # Locust load tests
│   └── production/           # Production smoke tests
├── docs/
│   ├── ARCHITECTURE.md       # System design
│   ├── PERFORMANCE.md        # Load test results
│   ├── MONITORING.md         # Production monitoring
│   └── RENDER_DEPLOYMENT.md  # Deployment guide
├── scripts/
│   ├── seed_database.py      # Database seeding
│   └── train_model.py        # ML model training
├── alembic/                  # Database migrations
├── Dockerfile                # Container definition
└── requirements.txt          # Python dependencies

---

## 🚀 Local Development

```bash
# 1. Clone repository
git clone https://github.com/danyon-satyam/ecp-2024.git
cd ecp-2024

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/sentiment_db"
export APP_NAME="Student Sentiment Analysis API"

# 5. Run database migrations
alembic upgrade head

# 6. Seed database
python scripts/seed_database.py --count 100

# 7. Start development server
uvicorn app.main:app --reload --port 8000

# 8. Open Swagger docs
open http://localhost:8000/docs
uvicorn app.main:app --reload
```

---

## 🧪 Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests with coverage
pytest --cov=app --cov-report=html

# Run specific test suites
pytest tests/unit/ -v                    # Unit tests
pytest tests/integration/ -v             # Integration tests
pytest tests/production/ -v              # Production smoke tests

# Run load tests (local)
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Run load tests (production)
locust -f tests/load/locustfile.py --host=https://sentiment-api-vpmz.onrender.com
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

---


## 📚 Documentation

Comprehensive documentation available in the `docs/` directory:

- **[Architecture Overview](docs/ARCHITECTURE.md)** — System design and component breakdown
- **[API Documentation](docs/API_DOCUMENTATION.md)** — Complete API reference
- **[Database Schema](docs/DATABASE_SCHEMA.md)** — Data model and indexing strategy
- **[Performance Testing](docs/PERFORMANCE.md)** — Load test results and optimization
- **[Monitoring Guide](docs/MONITORING.md)** — Observability and troubleshooting
- **[Deployment Runbook](docs/DEPLOYMENT_RUNBOOK.md)** — Production deployment procedures
- **[ADR-009](docs/adrs/ADR-009-render-deployment-platform.md)** — Deployment platform decision

**For Reviewers:**

- **[Demo Script](docs/DEMO_SCRIPT.md)** — Live demonstration walkthrough
- **[Q&amp;A Preparation](docs/QA_PREPARATION.md)** — Anticipated questions and answers

---

## 🤝 Contributing

This is an educational project for the ECP 2024 program. Not accepting external contributions.

---

## 📝 License

The Copyright is reserverd by the Developer.

---

## 👤 Developer

**Name: Satyam Mohapatra**

**Mentor:** Pramit Dash

**Program:** ECP 2024
