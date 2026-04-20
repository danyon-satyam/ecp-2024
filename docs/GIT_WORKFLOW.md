# Git Workflow Guide

**Project:** Student Sentiment Analysis API
**Author:** Danyon Satyam
**Mentor:** Pramit Dash

---

## Branch Structure

main          ← Production-ready code only
└── develop ← Integration branch (features merge here)
└── feature/xyz  ← Individual feature branches
└── fix/xyz      ← Bug fix branches
└── docs/xyz     ← Documentation branches
└── chore/xyz    ← Maintenance branches

---


## Daily Workflow

### Starting new work

```bash
# Always start from the latest develop
git checkout develop
git pull origin develop

# Create your feature branch
git checkout -b feature/your-feature-name

# Work on your feature...
# Make commits as you go
git add .
git commit -m "feat: add sentiment trend endpoint"
```

### Commit Message Format (Conventional Commits)

Every commit message must follow this format:

type: short description in present tense

Types:
feat     → new feature
fix      → bug fix
docs     → documentation
test     → adding tests
refactor → code change (no feature, no fix)
chore    → dependency updates, CI changes
perf     → performance improvement

Examples:

```bash
git commit -m "feat: add at-risk students analytics endpoint"
git commit -m "fix: resolve connection pool exhaustion under load"
git commit -m "test: add integration tests for visualisation endpoints"
git commit -m "docs: add ADR for Docker containerisation strategy"
git commit -m "perf: disable SQL echo in production mode"
```

### Opening a Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Go to GitHub → your repo → Pull Requests → New Pull Request
# Base: develop  ←  Compare: feature/your-feature-name
# Fill in the PR template
# Request review from: pramit-dash
```

### After PR is approved and merged

```bash
# Switch back to develop and pull the merged changes
git checkout develop
git pull origin develop

# Delete your local feature branch (it's merged, no longer needed)
git branch -d feature/your-feature-name
```

---

## Branch Naming Convention

| Type          | Example                            |
| ------------- | ---------------------------------- |
| Feature       | `feature/add-docker-support`     |
| Bug fix       | `fix/connection-pool-exhaustion` |
| Documentation | `docs/update-api-readme`         |
| Performance   | `perf/async-database-operations` |
| Chore         | `chore/update-catboost-version`  |
| Test          | `test/add-load-test-scenarios`   |

---

## What Pramit Reviews in PRs

Pramit (mentor/client) will review:

1. Does the code follow separation of concerns?
2. Are all new functions documented with Google-style docstrings?
3. Do tests cover the new functionality?
4. Is there an ADR if an architectural decision was made?
5. Does CI pass on this branch?
6. Are there any hardcoded secrets or credentials?

---

## Release Process

When `develop` has been tested and is ready for production:

```bash
git checkout main
git merge develop
git tag -a v1.0.0 -m "Release v1.0.0 — initial production deployment"
git push origin main --tags
```

Tags trigger the deployment pipeline to GCP (configured on Days 25-26).
