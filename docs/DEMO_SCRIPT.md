# Live Demo Script for Code Review

**Presenter:** Danyon Satyam
**Audience:** Pramit Dash (Mentor)
**Duration:** 10-15 minutes
**Date:** May 3, 2026 (7:30 PM IST / 4:00 PM CEST)

---

## 🎯 Demo Objectives

1. Show live production API with real data
2. Demonstrate all key features working correctly
3. Highlight architecture decisions and trade-offs
4. Showcase testing strategy and coverage
5. Discuss performance and scalability

---

## 📋 Pre-Demo Checklist (30 min before)

- [ ] API is live: https://sentiment-api-vpmz.onrender.com/health
- [ ] Database has ~500 records (check /analytics/summary)
- [ ] All visualization endpoints working
- [ ] Swagger UI loads correctly
- [ ] Browser tabs ready:
  - Tab 1: Swagger UI (https://sentiment-api-vpmz.onrender.com/docs)
  - Tab 2: GitHub repo (https://github.com/danyon-satyam/ecp-2024)
  - Tab 3: Render dashboard (https://dashboard.render.com/)
  - Tab 4: VS Code with code open
- [ ] Screen share tested
- [ ] Backup plan: Have cURL commands ready if Swagger fails

---

## 🎬 Demo Flow (10-15 minutes)

### Part 1: Quick Overview (2 min)

**Opening:**

> "Hi Pramit! Thanks for taking the time. I've built a Student Sentiment Analysis API that's currently live in production on Render. Let me show you what it can do, then we'll dive into the code."

**Show production URL:**

https://sentiment-api-vpmz.onrender.com/docs

**Key points:**

- "This is a fully functional REST API deployed on Render's free tier"
- "It uses FastAPI, PostgreSQL, and a CatBoost ML model"
- "Currently serving 500 student feedback records"
- "Auto-deployed from GitHub on every push to main"

---

### Part 2: Live API Demo (3-4 min)

**Use Swagger UI for all demos (visual, interactive)**

#### Test 1: Health Check

1. Click **GET /health**
2. Click **Try it out** → **Execute**
3. **Point out:** "This is what Render monitors every 30 seconds"

---

#### Test 2: Create Feedback (ML Prediction)

1. Click **POST /api/v1/feedback**
2. Click **Try it out**
3. Paste example:

```json
{
  "roll_number": "DEMO2024999",
  "gender": "Male",
  "age": 20,
  "study_hours_per_day": 8,
  "attendance_percentage": 92,
  "active_backlogs": 0,
  "academic_feedback": "Excellent",
  "emotional_feedback": "Happy"
}
```

4. Click **Execute**
5. **Point out:** "Notice the ML model predicted 'Positive' sentiment automatically"
6. **Show response time:** "~400-500ms including database write and ML prediction"

---

#### Test 3: Analytics

1. Click **GET /api/v1/analytics/summary**
2. Click **Try it out** → **Execute**
3. **Point out:**
   - "500 total students in production database"
   - "Sentiment distribution: ~36% Positive, 33% Neutral, 31% Negative"
   - "This query uses database indexes for fast aggregation (~120ms)"

---

#### Test 4: Visualization

1. Click **GET /api/v1/visualisations/sentiment-bar**
2. Click **Try it out** → **Execute**
3. **Point out:**

   - "Returns a PNG image (not JSON)"
   - "Generated with Matplotlib + Seaborn"
   - "Takes ~8 seconds (CPU bottleneck on free tier)"
4. **Open image in new tab** to show the actual chart

---

### Part 3: Architecture Walkthrough (3-4 min)

**Switch to VS Code**

#### Show Project Structure

ecp-2024/
├── app/
│   ├── api/v1/endpoints/     ← "REST API routes"
│   ├── models/               ← "SQLAlchemy ORM"
│   ├── schemas/              ← "Pydantic validation"
│   ├── services/             ← "Business logic + ML"
│   └── db/                   ← "Database session management"
├── tests/                    ← "93% coverage"
├── docs/                     ← "Comprehensive documentation"
└── Dockerfile                ← "Containerization"

#### Highlight Key Files

**1. Repository Pattern** (`app/services/feedback_repository.py`)

> "I used the repository pattern to separate database logic from API endpoints. This makes the code testable and swappable."

**2. ML Model Integration** (`app/services/sentiment.py`)

> "The ML model loads on startup and uses CatBoost for predictions. It falls back to rule-based logic if the model isn't loaded."

**3. Error Handling** (`app/core/exceptions.py` + `app/core/error_handlers.py`)

> "Custom exception classes with global error handlers ensure consistent error responses across the entire API."

---

### Part 4: Testing Strategy (2-3 min)

**Switch to terminal**

#### Show Test Coverage

```bash
pytest --cov=app --cov-report=term-missing
```

**Point out:**

- "93% test coverage"
- "Unit tests, integration tests, and load tests"
- "SQLite for testing (zero setup, fresh database per test)"

#### Show Test Categories

tests/
├── unit/           ← "Test functions in isolation"
├── integration/    ← "Test full request → response flow"
└── load/           ← "Locust performance testing"

**Run a quick test:**

```bash
pytest tests/integration/test_feedback_api.py::TestSubmitFeedback::test_submit_feedback_returns_201 -v
```

> "Tests run in CI on every push, blocking bad code from reaching production."

---

### Part 5: Deployment & DevOps (2 min)

**Switch to GitHub repo**

#### Show CI/CD Pipeline

1. Click **Actions** tab
2. Show latest workflow run (green checkmark)
3. **Point out:**
   - "Every push triggers: lint → test → coverage check"
   - "Only code that passes goes to main"

#### Show Render Dashboard

1. Open Render dashboard
2. Click **sentiment-api**
3. **Show Metrics tab:**
   - "CPU usage, memory, request count"
   - "Real-time monitoring"
4. **Show Logs tab:**
   - "Last 7 days of logs"
   - "Shows startup, migrations, ML model loading"

> "Auto-deployment from GitHub: push to main → Render builds Docker image → deploys with zero downtime in 3-5 minutes."

---

### Part 6: Performance Results (1-2 min)

**Switch to `docs/PERFORMANCE.md`**

**Show production metrics:**

Production (Render Free Tier):

* Throughput: ~12 RPS
* Avg Latency: ~600ms
* P95 Latency: ~3000ms
* Error Rate: <1%

**Point out bottleneck:**

> "Visualization endpoints are the bottleneck at 8-15 seconds. On the free tier with 0.1 vCPU, Matplotlib rendering is slow. This could be solved with caching or upgrading to a paid tier."

---

## 🎤 Closing Statement (30 seconds)

> "That's the live demo! The API is production-ready, fully tested, documented, and deployed with continuous delivery. I've learned a ton about FastAPI, ML model serving, Docker, and cloud deployment. Happy to dive into any part of the code or answer questions about architecture decisions."

---

## ❓ Anticipated Questions & Answers

### Q: Why Render instead of GCP?

**A:** "Based on your guidance to use free platforms without credit card requirements. Render offered 100% free tier with managed PostgreSQL. The Docker-based architecture means we could migrate to GCP in 2-3 hours if needed for production scale—I documented this migration path in ADR-009."

---

### Q: Why store sentiment in the database if it's ML-predicted?

**A:** "Denormalization for performance. Analytics queries hit the sentiment column frequently. Storing it means we can index it for fast GROUP BY queries (~120ms vs ~2 seconds if we had to recalculate on every query). The trade-off is we recalculate when records are updated—which happens rarely."

---

### Q: What's your test strategy?

**A:** "Three layers: Unit tests for business logic isolation, integration tests for full HTTP flows, and load tests for performance. 93% coverage. I use SQLite for tests—zero setup, fresh database per test. The trade-off is we don't test PostgreSQL-specific features, but that's acceptable for this scope."

---

### Q: How would you scale this beyond 20 concurrent users?

**A:**

1. Upgrade to Render paid tier ($7/mo, better CPU)
2. Add Redis for caching visualization endpoints (8s → 50ms for cache hits)
3. Horizontal scaling (2-3 containers behind load balancer)
4. For 1000+ users: Database read replicas, background workers (Celery), CDN

**"The architecture supports these because I used connection pooling, stateless containers, and Docker."**

---

### Q: Why CatBoost over simpler models?

**A:** "CatBoost handles categorical features (gender, academic_feedback) natively without one-hot encoding. It's also fast to train and predict. The accuracy gain over simpler models justified the ~50MB model size. I also included a rule-based fallback for environments where the model isn't loaded."

---

### Q: What would you do differently if starting over?

**A:**

1. Add response caching from Day 1 (not as afterthought)
2. Use async database operations (asyncpg) instead of sync
3. Implement API authentication earlier
4. Pre-generate charts on data updates instead of on-demand

**"That said, I'm happy with the repository pattern, error handling strategy, and test structure—those were solid decisions."**

---

## 🚨 Backup Plans

### If Swagger UI is slow/broken:

**Use cURL commands:**

```bash
# Health check
curl https://sentiment-api-vpmz.onrender.com/health

# Submit feedback
curl -X POST https://sentiment-api-vpmz.onrender.com/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{"roll_number":"DEMO999", "gender":"Male", "age":20, ...}'

# Analytics
curl https://sentiment-api-vpmz.onrender.com/api/v1/analytics/summary
```

---

### If API is down:

**Show:**

1. Local Docker deployment: `docker-compose up`
2. Test results: `pytest -v`
3. Code walkthrough instead of live demo
4. Explain: "Free tier sleeps after 15 min idle, cold start is ~30s—let me wake it up while we review the code"

---

### If questions go deep on one topic:

**Have these ready:**

- `app/services/feedback_repository.py` (Repository pattern)
- `tests/integration/test_feedback_api.py` (Integration tests)
- `docs/ARCHITECTURE.md` (System design)
- `docs/PERFORMANCE.md` (Load testing results)

---

## ⏱️ Time Management

| Section       | Time  | Hard Stop |
| ------------- | ----- | --------- |
| Overview      | 2 min | 2 min     |
| Live API Demo | 4 min | 6 min     |
| Architecture  | 3 min | 9 min     |
| Testing       | 2 min | 11 min    |
| Deployment    | 2 min | 13 min    |
| Performance   | 1 min | 14 min    |
| Closing       | 1 min | 15 min    |

**Buffer:** 5 minutes for questions during demo

---

## ✅ Post-Demo Checklist

After the meeting:

- [ ] Note all feedback from Pramit
- [ ] Update GitHub issues with any bugs/improvements mentioned
- [ ] Send thank-you email with meeting notes
- [ ] Update documentation based on feedback
- [ ] Implement any quick fixes discussed

---

**Practice:** Run through this 2-3 times before the meeting!
**Remember:** Stay calm, speak clearly, and have fun showing off your work! 🚀
