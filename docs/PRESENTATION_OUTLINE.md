# Code Review Presentation Outline

**Meeting:** Student Sentiment API Code Review
**Date:** May 3, 2026
**Time:** 7:30 PM IST (4:00 PM CEST)
**Duration:** 60 minutes
**Format:** Virtual (Google Meet / Zoom)

---

## 📋 Agenda (60 minutes)

### 1. Introduction & Context (3 min)

**Slide: Project Overview**

- **What:** REST API for university student sentiment analysis
- **Why:** Help universities identify at-risk students early
- **How:** FastAPI + PostgreSQL + CatBoost ML + Docker

**Key Stats:**

- 500 student records (production)
- 93% test coverage
- 12 RPS throughput (free tier)
- 15 endpoints (CRUD + analytics + visualizations)

---

### 2. Live Demo (12 min)

**No slides - just live interaction**

See `DEMO_SCRIPT.md` for detailed flow.

**Highlights:**

- Create feedback → ML prediction
- Analytics dashboard (summary)
- Visualization (charts)
- Show real production URL

---

### 3. Architecture Deep Dive (15 min)

**Slide: System Architecture**

GitHub → Render Build → Docker → FastAPI → PostgreSQL

**Topics:**

1. **Layered Architecture** (3 min)

   - API layer (routes)
   - Service layer (business logic)
   - Data layer (ORM)
   - "Separation of concerns enables testing and scalability"
2. **Repository Pattern** (2 min)

   - Why: Decouples database from business logic
   - Show code: `app/services/feedback_repository.py`
   - Benefit: Easy to mock for testing
3. **ML Model Integration** (3 min)

   - CatBoost model (85% accuracy)
   - Lazy loading on startup
   - Rule-based fallback
   - Show code: `app/services/sentiment.py`
4. **Error Handling** (2 min)

   - Custom exceptions (`RecordNotFoundException`)
   - Global error handlers
   - Consistent error responses
   - Show: `app/core/exceptions.py`
5. **Database Design** (2 min)

   - Single table (denormalized)
   - Indexed sentiment column
   - Why: Fast analytics queries
   - Trade-off: Storage vs speed
6. **Docker & Deployment** (3 min)

   - Dockerfile structure
   - Multi-stage build? (No - simple for free tier)
   - Auto-seed on startup
   - Show: `Dockerfile`

---

### 4. Testing Strategy (10 min)

**Slide: Test Pyramid**

E2E (none)
Integration (15 files)

Unit Tests (8 files)
Load Tests (Locust)

**Topics:**

1. **Unit Tests** (2 min)

   - Test business logic in isolation
   - Example: `test_sentiment.py`
   - Fast, deterministic
2. **Integration Tests** (3 min)

   - Full HTTP request flow
   - SQLite test database
   - Example: `test_feedback_api.py`
   - Show: How we mock the database
3. **Load Tests** (3 min)

   - Locust simulation (20 concurrent users)
   - Production results: 12 RPS, ~600ms avg
   - Bottleneck: Visualization rendering
   - Show: `locustfile.py`
4. **CI/CD Pipeline** (2 min)

   - GitHub Actions on every push
   - Runs: lint → test → coverage check
   - Show: `.github/workflows/ci.yml`

---

### 5. Performance & Scalability (8 min)

**Slide: Performance Metrics**

| Metric     | Local (4 workers) | Production (Free) |
| ---------- | ----------------- | ----------------- |
| RPS        | 29.4              | 12.0              |
| Latency    | 1401ms            | 600ms             |
| Error Rate | 0.0%              | 1.0%              |

**Topics:**

1. **Bottlenecks** (3 min)

   - Visualization endpoints: 8-15 seconds
   - Cause: Matplotlib CPU-intensive on 0.1 vCPU
   - Solution: Caching (Redis) or paid tier
2. **Optimizations Implemented** (2 min)

   - Database connection pooling
   - Indexed columns
   - ML model pre-loading
   - Efficient pagination
3. **Scaling Path** (3 min)

   - Current: 20 concurrent users max
   - For 100 users: Paid tier + Redis caching
   - For 1000 users: Horizontal scaling + CDN
   - Architecture supports this (stateless, Docker)

---

### 6. Q&A and Discussion (10 min)

**Open floor for Pramit's questions**

**Be ready to discuss:**

- Architecture decisions and trade-offs
- Why X instead of Y?
- How would you handle Z?
- What would you do differently?

**Common topics:**

- Async vs sync database operations
- Why denormalize sentiment?
- GCP vs Render decision
- Testing strategy rationale
- Deployment choices

---

### 7. Next Steps & Wrap-up (2 min)

**Topics:**

1. **Immediate improvements** (based on feedback)
2. **Days 27-30 deliverables**

   - Documentation complete
   - Presentation materials ready
   - Demo tested
3. **Thank you + Feedback**

   - Request specific areas for improvement
   - Ask about Feldstern GCP access (if relevant)
   - Next meeting plans (if any)

---

## 📊 Supporting Materials

### Screen Share Tabs (in order):

1. Swagger UI (live demo)
2. VS Code (code walkthrough)
3. GitHub repo (tests, CI/CD)
4. Render dashboard (monitoring)
5. PERFORMANCE.md (metrics)
6. ARCHITECTURE.md (diagrams)

---

### Documents to Reference:

- `docs/ARCHITECTURE.md` — System design
- `docs/PERFORMANCE.md` — Load test results
- `docs/API_DOCUMENTATION.md` — API reference
- `docs/DATABASE_SCHEMA.md` — Database design
- `docs/MONITORING.md` — Observability

---

## 🎯 Key Messages to Convey

1. **Production-Ready**

   - "This isn't a localhost demo—it's actually live on the internet"
   - "Auto-deploys from GitHub with zero downtime"
   - "Handling real data with real ML predictions"
2. **Well-Tested**

   - "93% coverage isn't accidental—testing was part of the design"
   - "Unit + integration + load tests cover different concerns"
   - "CI blocks bad code from reaching production"
3. **Scalable Architecture**

   - "Built with growth in mind, even on free tier"
   - "Repository pattern, connection pooling, indexes"
   - "Docker means we can move to GCP in a few hours"
4. **Documented**

   - "Every decision has an ADR or documentation"
   - "New developer could onboard in 30 minutes"
   - "Deployment runbook for production operations"
5. **Thoughtful Trade-offs**

   - "Denormalization for speed vs storage"
   - "SQLite for tests vs PostgreSQL in production"
   - "Free tier limitations vs cost savings"
   - "I can explain the 'why' behind every choice"

---

## 🎤 Speaking Tips

### Do:

- ✅ Speak confidently but not arrogantly
- ✅ Admit when you don't know something
- ✅ Ask clarifying questions before answering
- ✅ Use concrete examples from the code
- ✅ Connect back to real-world use cases

### Don't:

- ❌ Apologize for what you didn't do
- ❌ Oversell or exaggerate capabilities
- ❌ Get defensive about criticism
- ❌ Rush through slides to "get it over with"
- ❌ Use jargon without explaining it first

---

## ⏱️ Time Tracking

**Set a visible timer** for each section.

**If running long:**

- Skip "nice to have" examples
- Offer to dive deeper in follow-up
- Prioritize live demo + architecture

**If running short:**

- Go deeper on interesting questions
- Show additional code examples
- Discuss potential improvements

---

## ✅ Pre-Meeting Checklist (1 hour before)

Technical:

- [ ] API is live and responding
- [ ] All endpoints tested (Swagger UI)
- [ ] Screen share tested
- [ ] Backup cURL commands ready
- [ ] VS Code with project open
- [ ] All browser tabs open and loaded

Presentation:

- [ ] Demo script reviewed
- [ ] Key talking points memorized
- [ ] Questions & answers prepared
- [ ] Documents easily accessible

Environment:

- [ ] Quiet room, good lighting
- [ ] Camera + microphone tested
- [ ] Phone on silent
- [ ] Water nearby
- [ ] Notebook for notes

---

## 🎬 Opening Lines

**Option 1 (Confident):**

> "Hi Pramit! Thanks for meeting with me. I'm excited to show you what I've built—a production-ready sentiment analysis API that's live on the internet right now. Let's start with a quick demo, then we'll dive into the architecture."

**Option 2 (Collaborative):**

> "Hi Pramit! Thank you for the opportunity to present. I've been working on this for the past month following your guidance on deployment and testing. I'd love to show you what works, get your feedback on architecture decisions, and discuss how I could improve it."

**Option 3 (Direct):**

> "Hi Pramit! Ready when you are. Should I share my screen and start with the live demo, or would you prefer to see the architecture first?"

**Pick the style that feels natural to you!**

---

## 📝 Note-Taking During Meeting

**Capture:**

- Specific feedback on code
- Questions you couldn't answer
- Suggestions for improvement
- Areas Pramit seemed most interested in
- Action items for follow-up

**Send within 24 hours:**

- Thank you email
- Meeting notes summary
- Action items with timeline
- Any questions that came up

---

## 🚀 Contingency Plans

### If demo fails:

- Show local Docker deployment
- Walk through tests instead
- Focus on code architecture
- Use cURL commands as backup

### If questions go very technical:

- "Great question - let me show you the code"
- Pull up relevant file in VS Code
- Walk through the logic step-by-step
- Offer to send detailed write-up after

### If Pramit has limited time:

- **Priority 1:** Live demo (5 min)
- **Priority 2:** Architecture overview (5 min)
- **Priority 3:** Testing strategy (3 min)
- **Offer:** Send documentation for offline review

---

**Practice this 2-3 times before the meeting!**
**You've got this!** 🎯
