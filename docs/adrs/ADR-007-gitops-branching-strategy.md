# ADR-007: GitOps Branching Strategy

**Date:** 2026-04-14
**Status:** Accepted
**Author:** Danyon Satyam
**Reviewed by:** Pramit Dash

---

## Context

As the project grows and Pramit (client) needs to review code before
it reaches production, we need a structured approach to version control.
Pushing directly to main means there is no review checkpoint, no way
to isolate experimental work, and no audit trail of what changed and why.

---

## Decision

We adopt a **trunk-based development** variant with two persistent
branches and short-lived feature branches:

- `main` — production-ready code only, protected from direct pushes
- `develop` — integration branch where features merge first
- `feature/*`, `fix/*`, `docs/*` — short-lived branches (1-3 days max)

All changes to `main` and `develop` go through Pull Requests.
PRs require the CI pipeline to pass before merging.

---

## Reasons

**Code review gate:** Pramit can review every change before it reaches
production. This is the primary requirement for enterprise projects.

**Isolated work:** Feature branches mean experimental work never
breaks the main codebase. If a feature takes 3 days and breaks
halfway through, `develop` is unaffected.

**Audit trail:** Every merge commit in Git history shows what changed,
who reviewed it, and why. Essential for enterprise compliance.

**Conventional Commits:** Standardised commit messages make the
changelog automatic and the history readable by any developer.

---

## Consequences

- Direct pushes to `main` are disabled (GitHub branch protection)
- Every feature requires opening a PR — slightly more overhead
- PR template ensures consistency in how changes are described
- CI must pass on the branch before merge is allowed
- Pramit receives GitHub notifications when PRs are opened for review
