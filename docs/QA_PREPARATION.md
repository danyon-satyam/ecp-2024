# Q&A Preparation for Code Review

**Purpose:** Anticipate difficult questions and prepare thoughtful answers
**Audience:** Pramit Dash (Senior Engineer)
**Context:** 30-day project, student learning, production deployment

---

## 🎯 General Approach to Questions

### Framework: **STAR Method**

- **Situation:** What was the context?
- **Task:** What did you need to accomplish?
- **Action:** What did you do?
- **Result:** What was the outcome?

### Example:

**Q:** "Why did you use CatBoost instead of a simpler model?"

**A (STAR):**

- **S:** "I needed to predict sentiment from mixed categorical and numerical features"
- **T:** "The goal was >80% accuracy while keeping predictions fast"
- **A:** "I compared Logistic Regression (78% accuracy), Random Forest (82%), and CatBoost (85%). CatBoost handled categorical features natively without encoding"
- **R:** "CatBoost gave the best accuracy with acceptable model size (~50MB) and fast predictions (~50ms)"

---

## 🔥 Likely Technical Questions

### Q1: "Why Render instead of GCP? Doesn't it limit scalability?"

**Short Answer:**
"Based on your guidance to use free platforms without credit cards. Render offered managed PostgreSQL and Docker support for free—perfect for MVP/demo scope."

**Longer Answer:**
"I chose Render following your recommendation to avoid credit card requirements and keep it simple for MVP. The architecture is cloud-agnostic—Docker-based, environment-driven config, no vendor lock-in. I documented a migration path to GCP in ADR-009; it would take 2-3 hours:

1. Push image to GCP Artifact Registry
2. Create Cloud SQL instance
3. Deploy to Cloud Run
4. Update DATABASE_URL

The free tier limits scalability to ~20 concurrent users, but for a demo project, that trade-off was acceptable to avoid costs. If this were for production, I'd deploy to GCP with your team's account."

---

### Q2: "Why denormalize sentiment in the database? Why not calculate on-the-fly?"

**Short Answer:**
"Performance. Analytics queries hit sentiment frequently. Storing it enables indexing for fast GROUP BY queries."

**Longer Answer:**
"I denormalized sentiment for query performance. The `/analytics/summary` endpoint does `GROUP BY sentiment` on every request. With sentiment indexed:

- **Denormalized (current):** ~120ms
- **Calculated on-the-fly:** ~2000ms (predict 500 records on every query)

The trade-off is storage (one extra column) and re-calculation on updates. But updates are rare (students submit once, maybe edit later), while analytics queries are frequent (admins check dashboards constantly). I optimized for the common case."

---

### Q3: "Why SQLite for tests? Doesn't that hide PostgreSQL bugs?"

**Short Answer:**
"Fast, zero-setup, fresh database per test. The trade-off is we don't test PostgreSQL-specific features."

**Longer Answer:**
"SQLite for tests gives us:

- **Zero setup:** No server to run, no credentials
- **Speed:** Tests run in seconds (important for CI)
- **Isolation:** Fresh database per test (no shared state)

The trade-off is we don't test PostgreSQL-specific features like full-text search, JSONB, or advanced indexing. For this project, that's acceptable—we're not using those features.

If we were using PostgreSQL-specific features, I'd use `testing.postgresql` or Docker Compose to spin up a real PostgreSQL container for integration tests. But for this scope, SQLite + unit tests + manual production testing was the pragmatic choice."

---

### Q4: "Your visualization endpoints take 8-15 seconds. How would you fix that?"

**Short Answer:**
"Add response caching. Pre-generate charts on data updates instead of on-demand."

**Longer Answer:**
"Current bottleneck: Matplotlib rendering on 0.1 vCPU (free tier).

**Solutions, in order of impact:**

1. **Response caching (Redis)** — 1-2 hours implementation

   - Cache PNG responses with 5-minute TTL
   - First request: 8 seconds
   - Subsequent requests: 50ms (cache hit)
   - Expected: 95% cache hit rate (users view same charts repeatedly)
2. **Lower resolution** — 15 minutes

   - Reduce DPI from 100 to 75
   - Expected: 8s → 4s
3. **Background generation (Celery)** — 1 day

   - Pre-generate charts when data changes
   - Store in S3/Cloud Storage
   - Endpoint just returns the URL
   - Expected: <100ms
4. **Upgrade tier** — immediate

   - $7/mo for 1 vCPU (10x CPU)
   - Expected: 8s → 800ms

I'd start with #1 (caching) since it's high impact, low effort, and works with free tier."

---

### Q5: "Why async database operations? Or why NOT async?"

**Current:** We're using **sync** operations (SQLAlchemy with `Session`).

**Short Answer:**
"Sync operations work fine for this project's scale (~20 users). Async would help at higher scale."

**Longer Answer:**
"I used **synchronous** database operations because:

1. **Simplicity:** Easier to reason about, less complex code
2. **Libraries:** SQLAlchemy's sync API is more mature
3. **Scale:** At <20 concurrent users, sync is fast enough

**When async makes sense:**

- High concurrency (100+ simultaneous requests)
- I/O-bound operations (waiting on databases, external APIs)
- Need to handle 1000+ connections

**If I were to add async:**

- Use `asyncpg` instead of `psycopg2`
- Use SQLAlchemy 2.0's async API
- Change all route handlers to `async def`
- Expected gain: 2-3x throughput

But for this scope, sync was the pragmatic choice. Premature optimization is the root of all evil."

---

### Q6: "93% test coverage—what's NOT covered?"

**Short Answer:**
"Visualization rendering code and some error edge cases."

**Longer Answer:**
"The uncovered 7% is mostly:

1. **Matplotlib rendering code** in visualization service

   - Hard to test (requires mocking PIL, image buffers)
   - Low value (we test the endpoint returns PNG)
2. **Error handlers for rare scenarios**

   - Like database connection failures during startup
   - Hard to simulate in tests
3. **Main.py startup/shutdown hooks**

   - Events that run once on container start

**What IS covered (the important stuff):**

- All business logic (sentiment calculation, analytics)
- All API endpoints (CRUD, analytics, visualizations)
- All error paths (404, 422, validation errors)
- All database operations (create, read, update, delete)

100% coverage isn't the goal—covering critical paths is. The uncovered code is either low-risk or low-value to test."

---

### Q7: "How would you handle 1000 concurrent users?"

**Short Answer:**
"Horizontal scaling, caching, background workers, database read replicas."

**Longer Answer:**
**Current architecture supports scaling because:**

- Stateless containers (no in-memory sessions)
- Connection pooling (handles multiple requests)
- Docker (can deploy anywhere)

**Scaling plan for 1000 users:**

**Phase 1: Vertical Scaling** (~100 users)

- Upgrade to 2GB RAM, 2 vCPU ($25/mo)
- Add Redis caching (visualization endpoints)
- Expected: 50-100 RPS

**Phase 2: Horizontal Scaling** (~500 users)

- Deploy 3-5 containers behind load balancer
- Database connection pooling (10 connections × 5 containers = 50 total)
- Expected: 200-300 RPS

**Phase 3: Database Scaling** (~1000 users)

- Read replicas for analytics queries
- Write to primary, read from replicas
- Expected: 500-800 RPS

**Phase 4: Async Everything** (~5000 users)

- Async database operations (asyncpg)
- Background workers (Celery) for chart generation
- CDN for static chart images
- Expected: 2000+ RPS

**Cost estimate:** ~$100-200/mo for 1000 concurrent users."

---

### Q8: "What would you do differently if starting over?"

**Honest Answer:**
"A few things, but overall I'm happy with the architecture."

**Specifics:**

**What I'd keep:**

- Repository pattern (decoupled, testable)
- Error handling approach (custom exceptions, global handlers)
- Testing strategy (pyramid with 93% coverage)
- Documentation (ADRs, comprehensive guides)

**What I'd change:**

1. **Add caching from Day 1**

   - I added it as an "optimization" later
   - Should have been part of initial architecture
2. **Use async database operations**

   - Would help with scale
   - Not much harder to implement initially
3. **Implement authentication earlier**

   - I built it as "open API" for demo
   - Adding auth later requires retrofitting all endpoints
4. **Use Git LFS for ML models**

   - 50MB model files in repo isn't ideal
   - Git LFS would handle this better
5. **Add structured logging from start**

   - I added it late in the project
   - Should have been in the template

**But:** These are minor. The core architecture decisions (layering, separation of concerns, Docker, testing) were solid and would stay the same."

---

## 🤔 Difficult/Philosophical Questions

### Q: "What's the most challenging bug you encountered?"

**Short Answer:**
"Database connection pool exhaustion during load testing."

**Longer Answer:**
"During load testing with 100 concurrent users, the API started returning 500 errors after ~30 seconds. The logs showed 'TimeoutError: QueuePool limit exceeded'.

**Root cause:** SQLAlchemy's default pool size (5 connections) was too small. With 100 concurrent requests and ~200ms average query time, we needed more connections.

**Debugging process:**

1. Checked logs → saw connection pool errors
2. Reproduced locally with Locust
3. Profiled with `pool.status()` → confirmed pool exhaustion
4. Researched SQLAlchemy connection pooling

**Solution:**

- Increased pool_size from 5 to 10
- Added max_overflow to 20 (burst capacity)
- Added pool_pre_ping (verify connections before use)

**Result:** Load test passed at 100 users with <1% error rate.

**Lesson learned:** Always load test BEFORE production. This would have been catastrophic if discovered during a real traffic spike."

---

### Q: "How do you know your ML model is accurate in production?"

**Short Answer:**
"I don't have production monitoring yet—that's a gap."

**Longer Answer:**
"Honestly? Right now I don't. The model was trained offline with 85% accuracy, but I'm not tracking accuracy in production. That's a gap.

**What I'd add:**

1. **Logging:** Log every prediction with confidence scores
2. **Feedback loop:** Let admins flag incorrect predictions
3. **Metrics dashboard:** Track accuracy over time
4. **A/B testing:** Compare ML model vs rule-based fallback
5. **Retraining pipeline:** Retrain monthly with new data

**Why I didn't implement this:**

- Time constraints (30-day project)
- Not critical for demo/MVP
- Would be Day 1 priority for production

**I'd estimate:** 2-3 days to implement basic production monitoring."

---

### Q: "Why FastAPI instead of Django REST Framework?"

**Short Answer:**
"Performance, modern Python features (async, type hints), and automatic OpenAPI docs."

**Longer Answer:**
"I chose FastAPI because:

1. **Performance:** 3-5x faster than Django (ASGI vs WSGI)
2. **Type hints:** Pydantic validation via Python type hints
3. **Async support:** Native async/await (important for scale)
4. **OpenAPI docs:** Auto-generated Swagger UI
5. **Modern:** Built with Python 3.6+ features

**Trade-offs:**

- Django has bigger ecosystem (more packages)
- Django Admin is powerful (FastAPI has none)
- Django is more opinionated (good for large teams)

**For this project:**

- FastAPI's performance and simplicity won
- We don't need admin panel or Django ORM
- Type-safe validation was a huge win

If this were a large enterprise app with complex admin requirements, Django might be better. But for an API-first project, FastAPI was the right choice."

---

## 🎓 Learning/Growth Questions

### Q: "What did you learn from this project?"

**Short Answer:**
"Production deployment, Docker, cloud platforms, and testing strategies."

**Longer Answer:**
**Technical skills:**

- Docker containerization (Dockerfile, multi-stage builds)
- Cloud deployment (Render, understanding PaaS vs IaaS)
- ML model serving (loading, caching, fallbacks)
- Load testing (Locust, performance profiling)
- Database optimization (indexing, connection pooling)

**Process skills:**

- Writing ADRs (documenting decisions)
- CI/CD pipelines (GitHub Actions)
- Incremental development (days 1-30 structure)
- Production-first thinking (monitoring, errors, rollbacks)

**Biggest surprise:**
Visualization endpoints being the bottleneck. I thought database would be slow, but Matplotlib rendering at 8-15 seconds was the real issue. Taught me to always profile before optimizing.

**What I'd focus on next:**

- Kubernetes (for orchestration at scale)
- Observability (Datadog, Grafana, distributed tracing)
- Microservices architecture (when one service isn't enough)"

---

### Q: "If you had another 30 days, what would you build?"

**Short Answer:**
"Admin dashboard, real-time notifications, and predictive analytics."

**Longer Answer:**
**Weeks 5-6: Admin Dashboard**

- React frontend (or Streamlit for speed)
- Real-time charts with WebSockets
- Student search/filter interface
- Bulk import/export

**Weeks 7-8: Real-time Features**

- WebSocket endpoint for live updates
- Email notifications for at-risk students
- Slack integration for counselor alerts

**Weeks 9-10: Advanced Analytics**

- Predictive models (will this student fail?)
- Trend forecasting (sentiment over time)
- Recommendation engine (interventions)

**Weeks 11-12: Production Hardening**

- Authentication (API keys, JWT)
- Rate limiting (per user)
- Monitoring (Datadog integration)
- Automated backups
- Disaster recovery plan

**But:** I'm happy with what we accomplished in 30 days. Going deeper instead of wider was the right call."

---

## 😰 "I Don't Know" Questions

**It's okay to not know everything!**

### Good responses:

**"I don't know, but here's how I'd find out:"**

> "I don't know the exact syntax for PostgreSQL's full-text search, but I'd check the PostgreSQL docs for `to_tsvector` and `to_tsquery`. Want me to look that up real quick?"

**"I don't know, but here's my educated guess:"**

> "I'm not certain, but I believe SQLAlchemy's connection pool uses a queue-based approach where requests wait for available connections. Let me verify that in the docs if it's important for the discussion."

**"I don't know that specific detail, but here's the concept:"**

> "I don't remember the exact default pool size, but I know SQLAlchemy has configurable pool_size and max_overflow parameters. The defaults are conservative—I increased them during load testing."

**"That's outside my experience, but I'd love to learn:"**

> "I haven't worked with Kubernetes yet—that's on my learning list. How does it compare to Render for this kind of project?"

---

## 🎯 Redirect Questions

**If Pramit asks something tangential, redirect to what you know well:**

**Example:**

> Pramit: "What do you think about GraphQL vs REST?"
>
> You: "I don't have hands-on GraphQL experience, but I chose REST for this project because [reasons]. Would you like to discuss how I structured the REST endpoints and versioning?"

**This shows:**

- Honesty (you don't fake knowledge)
- Confidence (you redirect to your strengths)
- Control (you guide the conversation)

---

## ✅ Before the Meeting

Practice these out loud:

- [ ] Read through all Q&A answers
- [ ] Practice "I don't know" responses
- [ ] Prepare 2-3 questions to ask Pramit
- [ ] Review your demo script
- [ ] Check your documentation is up-to-date

**Remember:** Thoughtful answers > quick answers. It's okay to pause and think!

---

**Last Updated:** May 2, 2026
**Review this the night before the meeting!**
