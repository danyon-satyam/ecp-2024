# ADR-002: Test-Driven Development with Pytest

**Date:** 2026-04-09
**Status:** Accepted
**Author:** Danyon Satyam
**Reviewed by:** Pramit Dash

---

## Context

We needed a testing strategy for a production API that will handle
real university student data. The system must be reliable — bugs in
sentiment analysis could mislabel a struggling student as happy,
leading to missed intervention opportunities.

---

## Decision

We adopted **Test-Driven Development (TDD)** using **Pytest** as our
testing framework, following the RED → GREEN → REFACTOR cycle.

---

## Reasons

**Reliability:** With TDD, every feature has tests before it ships.
This means regressions (accidentally breaking old features) are caught
immediately — not discovered by university admins using the live system.

**Confidence when refactoring:** When we upgrade the ML model (Days 9-10),
our existing tests prove the API behaviour has not changed.

**Pytest simplicity:** Pytest requires minimal boilerplate. Tests are
plain functions starting with `test_`. Fixtures in `conftest.py` allow
reusable setup without repeating code across test files.

**FastAPI TestClient:** Allows full integration tests without starting
a real server — tests run in milliseconds, making TDD fast and practical.

---

## Consequences

- All new features must have tests written before or alongside the code
- The `tests/` folder is split into `unit/` and `integration/` layers
- `conftest.py` holds shared fixtures to avoid duplication
- CI pipeline (GitHub Actions) runs the full test suite on every push
