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

| Endpoint                                           | RPS            | Avg Latency | 95th Percentile | Fail Rate |
| -------------------------------------------------- | -------------- | ----------- | --------------- | --------- |
| GET /api/v1/analytics/at-risk                      | 2.0            | 346ms       | 930ms           | 0.0%      |
| GET /api/v1/analytics/by-sentiment                 | 1.7            | 293ms       | 1000ms          | 0.0%      |
| GET /api/v1/analytics/summary                      | 3.6            | 443ms       | 1300ms          | 0.0%      |
| GET /api/v1/analytics/trends                       | 3.0            | 326ms       | 1100ms          | 0.0%      |
| GET /api/v1/feedback                               | 0.8            | 209ms       | 660ms           | 0.0%      |
| GET /api/v1/feedback/all                           | 5.7            | 420ms       | 1200ms          | 0.0%      |
| POST /api/v1/feedback/setup                        | 0.8            | 172ms       | 550ms           | 0.0%      |
| POST /api/v1/feedback                              | 3.2            | 421ms       | 1100ms          | 0.0%      |
| GET [one] /api/v1/feedback/{id}                   | 3.4            | 428ms       | 1200ms          | 0.0%      |
| GET /api/v1/visualisations/attendance-vs-sentiment | 0.6            | 16783ms     | 26000ms         | 0.0%      |
| GET /api/v1/visualisations/gender-sentiment        | 0.6            | 5784ms      | 8800ms          | 0.0%      |
| GET /api/v1/visualisations/sentiment-bar           | 1.6            | 6779ms      | 11000ms         | 0.0%      |
| GET /api/v1/visualisations/sentiment-pie           | 0.9            | 7536ms      | 15000ms         | 0.0%      |
| GET /health                                        | 1.4            | 132ms       | 360ms           | 0.0%      |
| **TOTAL**                                    | **29.4** | **1401ms** | **8700ms**     | **0.0%** |

Total Requests : 1,742
Total Failures : 0
Overall Failure Rate: 0.00%
