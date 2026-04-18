# ADR-004: Faker and Polyfactory for Mock Data Generation

**Date:** 2026-04-11
**Status:** Accepted
**Author:** Danyon Satyam
**Reviewed by:** Pramit Dash

---

## Context

Development and testing require realistic student data. The real CSV
contains 351 student records from one university. For development,
load testing, and demonstrating the app to clients at other universities,
we need a way to generate large volumes of realistic student data quickly
without using real personal information (privacy concern).

---

## Decision

We use **Faker** for generating realistic fake values and
**Polyfactory** for generating complete valid Pydantic schema objects.

---

## Reasons

**Privacy compliance:** Real student data cannot be used in development
environments. Faker generates data that looks real but belongs to no one.

**Polyfactory + Pydantic integration:** ModelFactory automatically
respects all Pydantic validation rules. Generated data always passes
schema validation — no manual effort to keep factory in sync with schema
changes.

**Weighted distributions:** Faker allows weighted random choices so
generated data reflects realistic university patterns — most students
have 0 backlogs, most attendance is 60-90%, most feedback is Neutral
or Positive. This makes visualisations meaningful rather than uniform.

**Scale testing:** The seeder script can generate 1000+ records in
seconds, enabling load testing for the 100s of concurrent users target.

**Indian locale:** Faker's `en_IN` locale generates contextually
appropriate data for Indian universities matching our target client base.

---

## Consequences

- `scripts/seed_database.py` is the standard way to populate development databases
- All test fixtures that need student data use the factory, not hardcoded dicts
- Privacy: no real student data ever enters development or test environments
- The factory must be updated whenever the StudentFeedbackCreate schema changes
