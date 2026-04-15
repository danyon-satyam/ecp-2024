# ADR-001: Choice of FastAPI as Web Framework

**Date:** 2026-04-09
**Status:** Accepted
**Author:** Danyon Satyam
**Reviewed by:** Pramit Dash

---

## Context

We needed to choose a Python web framework to build a REST API that:

- Handles hundreds of concurrent university users
- Provides automatic data validation
- Generates interactive API documentation automatically
- Supports modern async programming for scalability
- Is easy for non-technical university admins to test via a browser UI

The main candidates considered were Flask, Django REST Framework, and FastAPI.

---

## Decision

We chose **FastAPI** as the web framework.

---

## Reasons

**Performance:** FastAPI is one of the fastest Python frameworks available,
built on Starlette and using async/await natively. This is critical for
handling hundreds of concurrent student feedback submissions.

**Automatic Swagger UI:** FastAPI generates an interactive `/docs` page
automatically from our code. University clients can test all API endpoints
without any technical knowledge — they just open the browser and click.

**Pydantic integration:** FastAPI uses Pydantic v2 for data validation
out of the box. Invalid data (wrong CGPA format, missing fields) is
rejected automatically with clear error messages before it reaches our
business logic.

**Type safety:** FastAPI uses Python type hints throughout. This catches
bugs at development time rather than production time.

**Industry adoption:** FastAPI is widely used in production ML and data
science APIs, making it a natural fit for our sentiment analysis use case.

---

## Alternatives Considered

**Flask:** Simpler but requires many extensions for validation, docs,
and async support. More setup work for the same result.

**Django REST Framework:** More batteries included but heavyweight for
an API-only project. Overkill for our use case and slower to develop with.

---

## Consequences

- All API routes must follow FastAPI patterns (router, dependency injection)
- Pydantic schemas must be defined for all request and response bodies
- The team must learn FastAPI-specific concepts (routers, depends, etc.)
- Swagger UI at `/docs` is available for free — no extra work needed
