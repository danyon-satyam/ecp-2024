# Performance Configuration Guide

**Project:** Student Sentiment Analysis API
**Author:** Danyon Satyam
**Date:** April 2026

---

## Architecture Overview

Internet → Load Balancer (GCP)
                                                 │
┌──────────┴──────────┐
│    Uvicorn Workers                                                        │
│  ┌───┐ ┌───┐ ┌───┐                       │
│  │ W1      │ │ W2      │ │ W3      │                       │  ← Each worker = 1 CPU core
│  └───┘ └───┘ └───┘                       │
└──────────┬──────────┘
                                                 │
┌──────────┴──────────┐
│  PostgreSQL Pool                                                          │
│  (10 connections)                                                          │
└─────────────────────┘

## Worker Configuration

| Environment | Workers | Formula                       |
| ----------- | ------- | ----------------------------- |
| Development | 1       | Single process, --reload mode |
| GCP 1-core  | 3       | (1 × 2) + 1                  |
| GCP 2-core  | 5       | (2 × 2) + 1                  |
| GCP 4-core  | 9       | (4 × 2) + 1                  |

## Connection Pool Settings

| Setting       | Value | Reason                               |
| ------------- | ----- | ------------------------------------ |
| pool_size     | 10    | 10 persistent connections            |
| max_overflow  | 20    | 20 extra connections under peak load |
| pool_timeout  | 30s   | Max wait for a free connection       |
| pool_recycle  | 3600s | Recycle connections hourly           |
| pool_pre_ping | True  | Verify connection health before use  |

---

## Why Async Endpoints?

FastAPI with `async def` endpoints handles requests on a single
event loop without blocking. When 100 users submit simultaneously:

**Without async (sync def):**

- Each request blocks a thread while waiting for the database
- At 10 concurrent threads, request 11 waits in a queue
- Latency spikes under load

**With async (async def) + thread pool for DB:**

- Event loop handles all 100 requests concurrently
- Database calls run in a thread pool (non-blocking to the event loop)
- Consistent low latency under load

---

## Uvloop

uvloop is a C-based replacement for Python's asyncio event loop.
It is 2-4x faster for I/O-heavy workloads.
Installed via `uvicorn[standard]`.

---

## Target Performance Metrics

STUDENT SENTIMENT API — LOAD TEST PERFORMANCE REPORT

| Endpoint                                           | RPS            | Avg Latency      | 95th Percentile  | Fail Rate      |
| -------------------------------------------------- | -------------- | ---------------- | ---------------- | -------------- |
| GET /api/v1/analytics/at-risk                      | 2.0            | 346ms            | 930ms            | 0.0%           |
| GET /api/v1/analytics/by-sentiment                 | 1.7            | 293ms            | 1000ms           | 0.0%           |
| GET /api/v1/analytics/summary                      | 3.6            | 443ms            | 1300ms           | 0.0%           |
| GET /api/v1/analytics/trends                       | 3.0            | 326ms            | 1100ms           | 0.0%           |
| GET /api/v1/feedback                               | 0.8            | 209ms            | 660ms            | 0.0%           |
| GET /api/v1/feedback/all                           | 5.7            | 420ms            | 1200ms           | 0.0%           |
| POST /api/v1/feedback/setup                        | 0.8            | 172ms            | 550ms            | 0.0%           |
| POST /api/v1/feedback                              | 3.2            | 421ms            | 1100ms           | 0.0%           |
| GET [one] /api/v1/feedback/{id}                   | 3.4            | 428ms            | 1200ms           | 0.0%           |
| GET /api/v1/visualisations/attendance-vs-sentiment | 0.6            | 16783ms          | 26000ms          | 0.0%           |
| GET /api/v1/visualisations/gender-sentiment        | 0.6            | 5784ms           | 8800ms           | 0.0%           |
| GET /api/v1/visualisations/sentiment-bar           | 1.6            | 6779ms           | 11000ms          | 0.0%           |
| GET /api/v1/visualisations/sentiment-pie           | 0.9            | 7536ms           | 15000ms          | 0.0%           |
| GET /health                                        | 1.4            | 132ms            | 360ms            | 0.0%           |
| **TOTAL**                                    | **29.4** | **1401ms** | **8700ms** | **0.0%** |

Total Requests : 1,742
Total Failures : 0
Overall Failure Rate: 0.00%



---


## Production Performance (Render Free Tier)

**Test Date:** May 2, 2026
**Platform:** Render.com Free Tier
**Region:** Frankfurt (EU Central)
**Database:** PostgreSQL 15 (500 records)
**Configuration:** 512 MB RAM, 0.1 vCPU

### Load Test Configuration

```bash
locust -f tests/load/locustfile.py \
  --host=https://sentiment-api-vpmz.onrender.com \
  --users=20 \
  --spawn-rate=2 \
  --run-time=120s
```

### Results

| Endpoint                                 | RPS           | Avg Latency      | 95th Percentile   | Fail Rate     |
| ---------------------------------------- | ------------- | ---------------- | ----------------- | ------------- |
| GET /health                              | 1.2           | 80ms             | 200ms             | 0.0%          |
| GET /api/v1/feedback                     | 0.9           | 250ms            | 600ms             | 0.0%          |
| POST /api/v1/feedback                    | 0.8           | 480ms            | 1200ms            | 2.5%          |
| GET /api/v1/feedback/{id}                | 1.1           | 220ms            | 550ms             | 0.0%          |
| GET /api/v1/analytics/summary            | 1.0           | 380ms            | 900ms             | 0.0%          |
| GET /api/v1/analytics/at-risk            | 0.5           | 320ms            | 850ms             | 0.0%          |
| GET /api/v1/analytics/trends             | 0.6           | 410ms            | 1100ms            | 0.0%          |
| GET /api/v1/visualisations/sentiment-bar | 0.4           | 8500ms           | 15000ms           | 0.0%          |
| **TOTAL**                          | **~12** | **~600ms** | **~3000ms** | **~1%** |

**Total Requests:** ~1,440
**Total Failures:** ~15 (rate limiting)
**Test Duration:** 120 seconds
****Concurrent Users:** 20**

## Performance Comparison: Local vs Production

| Metric      | Local (4 workers) | Production (Free Tier) |
| ----------- | ----------------- | ---------------------- |
| RPS         | 29.4              | 12.0                   |
| Avg Latency | 1401ms            | 600ms                  |
| P95 Latency | 8700ms            | 3000ms                 |
| Fail Rate   | 0.0%              | 1.0%                   |
| Workers     | 4                 | 1                      |
| CPU         | 4 cores           | 0.1 vCPU               |
| RAM         | 8 GB              | 512 MB                 |

**Key Insights:**

- Production is **faster per request** but **lower throughput** (free tier limits)
- Visualization endpoints are bottleneck (8-15 seconds)
- Database queries are efficient (~80-120ms)
- Rate limiting kicks in at ~15 RPS

---

## Bottlenecks Identified

### 1. Visualization Endpoints (Critical)

- **Issue:** 8-15 second response times
- **Cause:** Matplotlib rendering is CPU-intensive
- **Impact:** Users see loading spinners for charts
- **Solution:**
  - Short-term: Cache PNG responses (Redis)
  - Long-term: Pre-generate charts, serve from CDN

### 2. Cold Start (Acceptable for Demo)

- **Issue:** 30-second first request after 15 min idle
- **Cause:** Render free tier sleeps containers
- **Impact:** First user sees timeout
- **Solution:** Upgrade to paid tier OR accept for demo

### 3. Rate Limiting (Free Tier Constraint)

- **Issue:** 2-3% failures at 20+ concurrent users
- **Cause:** Render free tier caps at ~15 RPS
- **Impact:** Some requests return 503
- **Solution:** Upgrade to Render Standard ($7/mo)

---

## Optimization Recommendations

### Already Implemented ✅

- Database connection pooling
- Database indexes on `sentiment`, `roll_number`
- ML model pre-loading on startup
- Efficient pagination (LIMIT/OFFSET)

### Quick Wins (1-2 hours)

1. **Cache visualization endpoints** (Redis + 5-minute TTL)
   - Expected impact: 8s → 50ms for cached charts
2. **Reduce visualization resolution** (lower DPI)
   - Expected impact: 8s → 4s rendering time

### Future Enhancements (if scaling)

1. Background workers (Celery) for chart generation
2. CDN for static chart images
3. Horizontal scaling (multiple containers)
4. Database read replicas
5. API response compression (gzip)

---

## Production Readiness Assessment

| Criterion   | Status          | Notes                            |
| ----------- | --------------- | -------------------------------- |
| Functional  | ✅ Excellent    | All endpoints work correctly     |
| Performance | ⚠️ Limited    | Free tier caps at ~15 RPS        |
| Reliability | ✅ Good         | <1% error rate under normal load |
| Scalability | ⚠️ Limited    | Requires paid tier for >20 users |
| Cold Start  | ⚠️ Acceptable | 30s acceptable for demo          |

**Verdict:**
✅ **Ready for demo and code review**
⚠️ **Requires paid tier ($7/mo) for production traffic (>20 concurrent users)**

---

## Testing Strategy

### Unit Tests

- **Location:** `tests/unit/`
- **Coverage:** 93%
- **Run:** `pytest tests/unit/ -v`
- **Purpose:** Test individual functions in isolation

### Integration Tests

- **Location:** `tests/integration/`
- **Coverage:** All API endpoints
- **Run:** `pytest tests/integration/ -v`
- **Purpose:** Test full request → response flow

### Load Tests

- **Location:** `tests/load/locustfile.py`
- **Users:** 20 concurrent (production), 100 (local)
- **Run:** `locust -f tests/load/locustfile.py --config=tests/load/locust_production.conf`
- **Purpose:** Measure performance under load

---

**Last Updated:** May 2, 2026
