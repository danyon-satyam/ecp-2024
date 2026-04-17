# ADR-003: PostgreSQL as Primary Database with Repository Pattern

**Date:** 2026-04-10
**Status:** Accepted
**Author:** Danyon Satyam
**Reviewed by:** Pramit Dash

---

## Context

The project requires persistent storage for student feedback records
from potentially thousands of students across multiple universities.
The data is structured with fixed columns (CGPA, attendance, feedback
categories). Analytics queries (sentiment distribution, aggregations)
are needed for dashboards. GCP deployment is the target environment.

MongoDB was initially considered as the production database.

---

## Decision

We chose **PostgreSQL** as the primary database, accessed via
**SQLAlchemy ORM**, with the **Repository Pattern** as the
data access abstraction layer.

---

## Reasons

**Structured data fit:** Every student record has identical fixed fields.
This is textbook relational data — PostgreSQL's strength. MongoDB's
flexible schema provides no benefit here and adds unnecessary complexity.

**Analytics queries:** Pramit's requirements include sentiment
visualisations and aggregations across thousands of records.
PostgreSQL's query engine handles GROUP BY, COUNT, and aggregations
far more efficiently than MongoDB for structured data.

**GCP deployment:** Google Cloud SQL for PostgreSQL is a fully managed
service on GCP — simple setup, automatic backups, and well-documented.
MongoDB on GCP requires a separate Atlas account with additional
configuration complexity.

**Repository Pattern for flexibility:** Despite choosing PostgreSQL now,
the Repository Pattern ensures the database is completely swappable.
All database operations go through FeedbackRepository. If MongoDB
becomes a requirement later, only this one file needs rewriting.
No endpoints, schemas, or tests change.

---

## Consequences

- SQLAlchemy ORM is used for all database access (no raw SQL)
- All CRUD operations go through FeedbackRepository only
- Tests use SQLite in-memory database — no PostgreSQL needed for testing
- Environment variables manage all database credentials
- Switching to MongoDB in future requires rewriting only the repository
