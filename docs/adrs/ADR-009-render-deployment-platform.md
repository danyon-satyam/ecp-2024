# ADR-009: Render.com as Deployment Platform

**Date:** April 28, 2026
**Status:** Accepted
**Author:** Danyon Satyam
**Reviewed by:** Pramit Dash

---

## Context

The application requires production deployment for demonstration and code review purposes. The original plan was Google Cloud Platform (Cloud Run + Cloud SQL), but mentor feedback indicated:

1. GCP might be "overkill" for an MVP/demo project
2. Free or open-source solutions preferred (no credit card requirement)
3. Focus should be on deployment workflows, not platform complexity

---

## Decision

We deploy to **Render.com** using their free tier:

- Render Web Service (Docker container) — Free forever
- Render PostgreSQL — Free for 90 days
- Auto-deployment from GitHub via webhooks

---

## Reasons

**Mentor Recommendation:**
Pramit Dash specifically recommended evaluating free platforms and mentioned Render-like platforms as appropriate for this project scope.

**No Cost Barrier:**

- 100% free tier with no credit card required
- Removes financial concerns for student project
- GCP required credit card even for free trial

**Simplicity:**

- Web-based dashboard only (no CLI installation required)
- Docker deployment just works (existing Dockerfile unchanged)
- 30-minute setup vs. 3-4 hours for GCP

**Professional Enough:**

- Used by production companies (not just student projects)
- Auto-SSL, managed PostgreSQL, automatic backups
- Real production deployment experience, not localhost demo

**Continuous Delivery:**

- Auto-deploys on push to `main` branch
- Zero-downtime deployments
- Matches enterprise GitOps practices

**Docker-Native:**

- Reads Dockerfile directly from repository
- No need for container registry (GCP Artifact Registry)
- No need for model storage service (GCP Cloud Storage)
- ML models included in Docker image (~50MB is acceptable)

---

## Alternatives Considered

**Google Cloud Platform (Original Plan):**

- ❌ Requires credit card (even for free tier)
- ❌ More complex setup (gcloud CLI, multiple services)
- ❌ $7-15/month after free trial expires
- ✅ More enterprise-relevant for interviews
- ✅ Better scalability for production traffic

**Verdict:** Rejected due to cost and complexity for MVP scope

**Dokploy / Coolify:**

- ❌ Require self-hosting (need a VPS to run them)
- ❌ Additional complexity (managing the orchestrator itself)
- ❌ Not actually "free" (VPS costs $5-10/month)
- ✅ More control and flexibility

**Verdict:** Rejected — adds unnecessary complexity

**Fly.io:**

- ⚠️ Mentor specifically said "watch their pricing"
- ❌ Requires credit card for free tier
- ❌ Easy to accidentally exceed free limits
- ✅ Excellent platform with global edge network

**Verdict:** Rejected due to pricing concerns

**Vercel + Supabase:**

- ✅ 100% free
- ❌ Requires refactoring to serverless (can't use Docker)
- ❌ Not appropriate for this architecture

**Verdict:** Rejected — architectural mismatch

---

## Trade-offs Accepted

**PostgreSQL Expires After 90 Days:**

- Free PostgreSQL is time-limited
- Migration required at Day 90 (to Supabase or paid tier)
- **Mitigation:** Calendar reminder at Day 85, export data before expiry

**Free Tier Limitations:**

- 512MB RAM (vs 1GB+ on GCP)
- Container sleeps after 15 min idle (30s cold start)
- Not suitable for high-traffic production
- **Mitigation:** Acceptable for demo/review purposes

**Less Enterprise-Relevant:**

- In job interviews, "deployed to GCP" sounds more impressive
- Render is less common in large enterprises
- **Mitigation:** Docker skills and deployment workflows are transferable to any platform

---

## Migration Path to GCP (If Needed)

The Docker-based architecture is cloud-agnostic. Migration to GCP requires:

1. Build and push image to GCP Artifact Registry
2. Create Cloud SQL instance
3. Update DATABASE_URL
4. Deploy to Cloud Run
5. Run migrations

**Estimated migration time:** 2-3 hours

**Code changes required:** Zero (same Dockerfile works)

All GCP documentation from Days 21-23 (original plan) remains valid and can be executed if needed for interviews or production scaling.

---

## Success Criteria

Deployment considered successful when:

- [X] API accessible via public HTTPS URL
- [X] All endpoints functional (CRUD, analytics, visualizations)
- [X] Database persists data reliably
- [X] Auto-deployment from GitHub works
- [X] Zero-downtime deployments verified
- [X] Health checks passing
- [X] Demo-ready with seeded data

---

## Lessons Learned

**For Future Projects:**

- Start with simplest viable platform
- Can always migrate to more complex infrastructure later
- Free tiers are sufficient for MVPs and demos
- Docker containerization enables platform flexibility

---

## References

- Pramit Dash email (April 28, 2026): Deployment platform guidance
- Render Documentation: https://render.com/docs
- Original GCP plan: `docs/GCP_DEPLOYMENT_GUIDE.md` (archived for reference)
