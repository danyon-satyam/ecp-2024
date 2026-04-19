# ADR-006: Async Endpoints + Multi-Worker Uvicorn for Concurrency

**Date:** 2026-04-13
**Status:** Accepted
**Author:** Danyon Satyam
**Reviewed by:** Pramit Dash

---

## Context

Pramit's requirements specify handling "100s of concurrent users."
The initial implementation used synchronous `def` endpoints with a
single Uvicorn worker — adequate for development but insufficient
for production scale.

---

## Decision

We adopted two complementary strategies:

1. **Async endpoint functions (`async def`)** — allows FastAPI's event
   loop to handle concurrent requests without blocking between I/O operations
2. **Multi-worker Uvicorn** — spawns one worker process per CPU core,
   using all available hardware parallelism

---

## Why Not Full Async SQLAlchemy?

Full async SQLAlchemy with asyncpg requires rewriting all ORM queries
with `async/await` syntax and a completely different session management
pattern. The performance gain for queries under 50ms (our typical case)
is minimal compared to the code complexity increase.

FastAPI automatically runs synchronous `Depends(get_db)` in a thread
pool when called from `async def` endpoints — giving us non-blocking
behaviour for database I/O without rewriting the entire ORM layer.

Full async SQLAlchemy is appropriate when:

- Queries regularly exceed 100ms
- The application makes many concurrent DB calls per request
- The team is comfortable with async SQLAlchemy patterns

---

## Connection Pool Justification

pool_size=10, max_overflow=20 (total 30 connections maximum):

- With 4 workers and pool_size=10, total possible connections = 40
- PostgreSQL default max_connections=100 — well within limits
- At 100 concurrent users, average connection hold time ~20ms
  → 100 users × 20ms = 2,000ms of total DB time per second
  → 10 connections × 1,000ms = 10,000ms capacity per second
  → We have 5x headroom before pool exhaustion

---

## Load Test Results

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

## Consequences

- All endpoint functions must be `async def` going forward
- `scripts/start_server.py` is the standard way to start production server
- Worker count set via `WORKERS` environment variable
- Development still uses `uvicorn app.main:app --reload` (single worker)
- Load test results stored in `tests/load/results/` for reference
