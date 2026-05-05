# System Architecture

**Project:** Student Sentiment Analysis API
**Version:** 1.0.0
**Deployment:** Production (Render.com)
**Last Updated:** May 2, 2026

---

## 🏗️ High-Level Architecture

┌─────────────────────────────────────────────────────────┐
│                                                                                                               GitHub Repository                                                                                                         │
│                                                                                                                (Source of Truth)                                                                                                           │
│                                                                                                                                                                                                                                                              │
│                                                                     main (production) ←── develop ←── feature/* branches                                                             │
└──────────────────────┬──────────────────────────────────┘
                                                                                                       │
                                                                                                       │ Webhook on push to main
                                                                                                       ▼
                                                                 ┌────────────────┐
                                                                 │                     Render Build                        │
                                                                 │  (Docker)                                                    │
                                                                 └───────┬────────┘
                                                                                                     │
                                                                                                     │ Builds image from Dockerfile
                                                                                                     ▼
             ┌────────────────────────────────────────┐
             │    Docker Container (sentiment-api)                                                                                                          │
             │                                                                                                                                                                                   │
             │  ┌───────────────────────────────────┐            │
             │  │  FastAPI Application                                                                                                                  │            │
             │  │  • REST API (OpenAPI 3.1)                                                                                                     │            │
             │  │  • Pydantic Validation                                                                                                             │            │
             │  │  • SQLAlchemy ORM                                                                                                                │            │
             │  │  • CatBoost ML Model                                                                                                             │            │
             │  └──────────┬────────────────────────┘            │
             │                                                   │                                                                                                                            │
             │                                PostgreSQL Protocol                                                                                                         │
             │                                                   ▼                                                                                                                            │
             │  ┌───────────────────────────────────┐            │
             │  │  Connection Pool                                                                                                                        │            │
             │  │  • 10 persistent connections                                                                                                │            │
             │  │  • 20 overflow connections                                                                                                  │             │
             │  └─────────────────┬─────────────────┘             │
             └───  ───────────────┼─────────────────────┘
                                                                                                    │
                                                                                                    │ Internal network (secure)
                                                                                                    ▼
                                                               ┌────────────────┐
                                                               │  PostgreSQL 15                                       │
                                                               │  (sentiment-db)                                      │
                                                               │                                                                       │
                                                               │  • 500 records                                       │
                                                               │  • Indexed                                               │
                                                               │  • Managed                                             │
                                                               └────────────────┘

---

## 🔄 Request Flow (Complete Lifecycle)

1. Client Request
   │
   ├─ HTTPS → Render Load Balancer (SSL termination)
   │
   ▼
2. Container (Port 10000)
   │
   ├─ Uvicorn (ASGI Server)
   │   └─ 1 worker process (free tier)
   │
   ▼
3. Middleware Stack
   │
   ├─ CORS Middleware
   ├─ Error Handler Middleware (app/core/error_handlers.py)
   │
   ▼
4. FastAPI Router
   │
   ├─ Route Matching (app/api/v1/endpoints/)
   ├─ Dependency Injection (get_db session)
   ├─ Pydantic Validation (app/schemas/)
   │
   ▼
5. Service Layer
   │
   ├─ Business Logic
   ├─ ML Predictions (app/services/sentiment.py)
   ├─ Repository Calls (app/services/feedback_repository.py)
   │
   ▼
6. Data Layer
   │
   ├─ SQLAlchemy ORM (app/models/student_feedback.py)
   ├─ Database Session (from connection pool)
   ├─ SQL Query Execution
   │
   ▼
7. PostgreSQL Database
   │
   ├─ Query Execution
   ├─ Transaction Commit
   │
   ▼
8. Response Path
   │
   ├─ ORM → Pydantic Model (app/schemas/student.py)
   ├─ JSON Serialization
   ├─ HTTP Response (status code + headers + body)
   │
   ▼
9. Client receives JSON

---

## 📦 Component Breakdown

### API Layer (`app/main.py`, `app/api/`)

**Responsibilities:**

- HTTP request/response handling
- OpenAPI documentation generation
- Dependency injection
- Middleware orchestration

**Key Files:**

- `app/main.py` — Application factory, middleware setup
- `app/api/v1/endpoints/feedback.py` — CRUD operations
- `app/api/v1/endpoints/analytics.py` — Analytics aggregations
- `app/api/v1/endpoints/visualisations.py` — Chart generation

**Technologies:**

- FastAPI 0.111.0
- Uvicorn 0.29.0 (ASGI server)
- Pydantic 2.7.1 (validation)

---

### Service Layer (`app/services/`)

**Responsibilities:**

- Business logic
- ML model predictions
- Data transformations
- Analytics calculations

**Key Files:**

- `app/services/sentiment.py` — ML predictions + rule-based fallback
- `app/services/feedback_repository.py` — Database operations
- `app/services/analytics_service.py` — Aggregation logic
- `app/services/visualization_service.py` — Chart generation

**Technologies:**

- CatBoost 1.2.5 (ML model)
- Matplotlib 3.8.4 (charts)
- Seaborn 0.13.2 (chart styling)

---

### Data Layer (`app/models/`, `app/db/`)

**Responsibilities:**

- ORM mapping
- Database session management
- Connection pooling
- Migrations

**Key Files:**

- `app/models/student_feedback.py` — SQLAlchemy ORM model
- `app/db/database.py` — Engine + session factory
- `alembic/versions/` — Database migrations

**Technologies:**

- SQLAlchemy 2.0.30
- Alembic 1.13.1 (migrations)
- PostgreSQL 15

---

### ML Model Layer (`app/ml/`)

**Files:**

- `app/ml/sentiment_model.joblib` — Trained CatBoost model
- `app/ml/label_encoders.joblib` — Categorical encoders
- `app/services/sentiment.py` — Model loading + prediction

**Model Details:**

- **Algorithm:** CatBoost Classifier
- **Features:** `emotional_feedback`, `academic_feedback`, `study_hours_per_day`, `attendance_percentage`, `active_backlogs`, `gender`, `age`
- **Target:** `sentiment` (Positive, Neutral, Negative)
- **Accuracy:** ~85% (from training)
- **Loading Time:** ~8 seconds on cold start

---

## 🗄️ Database Schema

```sql
Table: student_feedback
┌──────────────────────────┬─────────────────┬────────────────┐
│ Column                   │ Type            │ Constraints    │
├──────────────────────────┼─────────────────┼────────────────┤
│ id                       │ SERIAL          │ PRIMARY KEY    │
│ roll_number              │ VARCHAR(50)     │ UNIQUE, NOT NULL│
│ gender                   │ VARCHAR(10)     │ NOT NULL       │
│ age                      │ INTEGER         │ NOT NULL       │
│ study_hours_per_day      │ INTEGER         │ NOT NULL       │
│ attendance_percentage    │ FLOAT           │ NOT NULL       │
│ active_backlogs          │ INTEGER         │ NOT NULL       │
│ academic_feedback        │ VARCHAR(50)     │ NOT NULL       │
│ emotional_feedback       │ VARCHAR(50)     │ NOT NULL       │
│ sentiment                │ VARCHAR(20)     │ NOT NULL       │
│ created_at               │ TIMESTAMP       │ DEFAULT NOW()  │
│ updated_at               │ TIMESTAMP       │ DEFAULT NOW()  │
└──────────────────────────┴─────────────────┴────────────────┘

Indexes:
  PRIMARY KEY, btree (id)
  UNIQUE, btree (roll_number)
  btree (sentiment)        -- For analytics queries

Foreign Keys: None (single-table design)
```

**Why This Schema:**

- **id:** Auto-incrementing surrogate key
- **roll_number:** Natural key (business identifier)
- **sentiment:** Denormalized (stored, not calculated) for fast queries
- **Timestamps:** Audit trail for created/updated

**Constraints:**

```sql
CHECK (age >= 17 AND age <= 35)
CHECK (attendance_percentage >= 0.0 AND attendance_percentage <= 100.0)
CHECK (active_backlogs >= 0)
```

---

## 🧪 Testing Architecture

**Test Coverage:** 93%

**Test Structure:**

tests/
├── unit/                      # Fast, isolated tests
│   ├── test_sentiment.py      # ML prediction logic
│   ├── test_mock_data.py      # Data generation
│   └── test_exceptions.py     # Error handling
├── integration/               # Full HTTP request flow
│   ├── test_feedback_api.py   # CRUD endpoints
│   ├── test_analytics_api.py  # Analytics endpoints
│   └── test_visualisations_api.py # Chart endpoints
└── load/                      # Performance tests
└── locustfile.py          # Concurrent user simulation

**Test Database:**

- **Type:** SQLite (in-memory)
- **Why:** Zero setup, instant reset, never touches production
- **Trade-off:** Doesn't test PostgreSQL-specific features

---

## 🔐 Security Architecture

┌────────────────────────────────────────┐
│  HTTPS (TLS 1.3)                                                                                                                                                │
│  • Render auto-SSL (Let's Encrypt)                                                                                                          │
│  • Certificate auto-renewal                                                                                                                         │
│  • A+ SSL Labs rating                                                                                                                                     │
└────────────┬───────────────────────────┘
                                                          │
                                                          ▼
┌────────────────────────────────────────┐
│  Environment Variables                                                                                                                                 │
│  • Encrypted at rest (Render)                                                                                                                    │
│  • Never committed to Git                                                                                                                          │
│  • Injected at runtime                                                                                                                                   │
└────────────┬───────────────────────────┘
                                                          │
                                                          ▼
┌────────────────────────────────────────┐
│  Database Security                                                                                                                                           │
│  • Internal network only (no public IP)                                                                                                  │
│  • Password-protected                                                                                                                                 │
│  • Connection pooling (limit 10)                                                                                                              │
└────────────────────────────────────────┘

**Current Security Posture:**

- ✅ HTTPS enforced
- ✅ Secrets in environment variables
- ✅ Database not publicly accessible
- ✅ Input validation (Pydantic)
- ⚠️ No authentication (demo API, public access)
- ⚠️ No rate limiting (Render provides basic protection)

**For Production:**

- Add API key authentication
- Implement request rate limiting
- Add CORS restrictions
- Set up WAF (Web Application Firewall)

---

## 🚀 Deployment Pipeline

Developer
│
│ git push origin feature/xyz
▼
GitHub (feature branch)
│
│ Open Pull Request
▼
CI Pipeline (GitHub Actions)
│
├─ Run pytest (unit + integration)
├─ Check coverage (>80%)
├─ Lint with flake8
│
▼
PR Approved & Merged to develop
│
│ Manual merge to main
▼
GitHub (main branch)
│
│ Webhook trigger
▼
Render Build System
│
├─ Clone repository
├─ docker build -t sentiment-api .
├─ Push image to registry
│
▼
Render Deploy
│
├─ Pull new image
├─ Run health checks
├─ Route traffic (zero downtime)
├─ Terminate old version
│
▼
Production (Live)
│
├─ alembic upgrade head (migrations)
├─ python scripts/seed_database.py --count 500
├─ uvicorn app.main:app --port 10000

**Deployment Metrics:**

- **Frequency:** On every push to `main` (continuous deployment)
- **Duration:** 3-5 minutes
- **Downtime:** 0 seconds (rolling deployment)
- **Rollback:** One-click in Render dashboard

---

## 📈 Scalability Path

**Current (Free Tier):**

- 1 container, 512 MB RAM, 0.1 vCPU
- ~15 RPS capacity
- ~20 concurrent users

**Scaling to 100 Users:**

1. Upgrade to Render Standard ($7/mo)

   - 512 MB → 2 GB RAM
   - 0.1 → 1 vCPU
   - No sleep (always-on)
   - Expected: 50-100 RPS
2. Add Redis caching

   - Cache visualization endpoints (5-min TTL)
   - Expected: 8s → 50ms for cached charts
3. Horizontal scaling

   - 2-3 containers (load balanced)
   - Expected: 150-300 RPS

**Scaling to 1,000 Users:**

1. Database read replicas
2. Background workers (Celery)
3. CDN for static assets
4. API response compression

---

## 🔧 Configuration

**Environment Variables:**

```bash
DATABASE_URL        # PostgreSQL connection string (secret)
APP_NAME            # "Student Sentiment Analysis API"
DEBUG               # False (production)
API_V1_PREFIX       # "/api/v1"
```

**Dockerfile Configuration:**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD alembic upgrade head && \
    python scripts/seed_database.py --count 500 || true && \
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
```

---

## 📊 Resource Utilization

**Measured on Production (May 2, 2026):**

| Resource     | Allocated | Used (Avg) | Used (Peak) |
| ------------ | --------- | ---------- | ----------- |
| RAM          | 512 MB    | 320 MB     | 450 MB      |
| CPU          | 0.1 vCPU  | 40%        | 85%         |
| Database     | 1 GB      | 85 MB      | 90 MB       |
| Docker Image | N/A       | 450 MB     | 450 MB      |

**Bottleneck:** CPU during visualization rendering

---

## 🎯 Architecture Principles

1. **Separation of Concerns:**

   - API layer (routes) doesn't know about databases
   - Service layer (business logic) is reusable
   - Data layer (ORM) is abstracted
2. **Dependency Injection:**

   - Database sessions injected via FastAPI
   - Easy to swap implementations (SQLite ↔ PostgreSQL)
3. **Cloud-Agnostic:**

   - Docker-based deployment works on any platform
   - Can migrate to GCP, AWS, Azure in 2-3 hours
4. **Test-Driven:**

   - 93% test coverage
   - Tests run in CI before deployment
5. **12-Factor App Compliance:**

   - ✅ Codebase (Git)
   - ✅ Dependencies (requirements.txt)
   - ✅ Config (env vars)
   - ✅ Backing services (PostgreSQL)
   - ✅ Build, release, run (Docker)
   - ✅ Stateless processes
   - ✅ Port binding (Uvicorn)
   - ✅ Logs (stdout)

---

**Last Updated:** May 2, 2026
**Author:** Satyam Mohapatra
**Reviewer:** Pramit Dash
