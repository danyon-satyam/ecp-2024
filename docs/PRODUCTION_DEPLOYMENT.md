# Production Deployment Details

**Project:** Student Sentiment Analysis API
**Deployed:** April 28, 2026
**Platform:** Render.com (Free Tier)
**Region:** Frankfurt, EU Central

---

## Live URLs

**Production API:**

[https://sentiment-api-xxxx.onrender.com](https://sentiment-api-xxxx.onrender.com)

**Swagger UI (API Documentation):**

[https://sentiment-api-xxxx.onrender.com](https://sentiment-api-xxxx.onrender.com)/docs

**Health Check:**

https://sentiment-api-xxxx.onrender.com/health

**ReDoc (Alternative Docs):**

https://sentiment-api-xxxx.onrender.com/redoc

---



## Infrastructure

| Component          | Service                      | Configuration                      |
| ------------------ | ---------------------------- | ---------------------------------- |
| API Server         | Render Web Service           | 512MB RAM, Docker container        |
| Database           | Render PostgreSQL            | PostgreSQL 15, free tier (90 days) |
| ML Model           | Included in Docker image     | CatBoost model (~50MB)             |
| Secrets            | Render Environment Variables | DATABASE_URL, APP_NAME, DEBUG      |
| Container Registry | Render Build System          | Auto-builds from GitHub            |
| Region             | Frankfurt (EU Central)       | Low latency to Europe              |

---

## Deployment Architecture

GitHub (main branch)
│
│ Push triggers webhook
▼
Render Build System
│
├─ Clones repo
├─ Builds Docker image from Dockerfile
├─ Runs health checks
│
▼
Render Web Service
│
├─ Port: 10000 (internal)
├─ HTTPS: Auto-SSL certificate
├─ Health check: /health every 30s
│
▼
Render PostgreSQL
│
├─ Internal connection via DATABASE_URL
├─ Automatic daily backups (7 day retention)

---


## Database

**Connection:** Internal Render PostgreSQL
**Database Name:** `sentiment_db`
**User:** `sentiment_user`
**Migrations:** Managed via Alembic
**Seeded Records:** 500 realistic student feedback entries

---

## Environment Variables

Set in Render Dashboard → sentiment-api → Environment:

```bash
DATABASE_URL=postgres://sentiment_user:***@dpg-xxxxx/sentiment_db
APP_NAME=Student Sentiment Analysis API
DEBUG=False
API_V1_PREFIX=/api/v1
```

---

## Deployment Process

**Automatic (Preferred):**

1. Push code to `main` branch on GitHub
2. Render detects webhook from GitHub
3. Render pulls latest code
4. Render builds Docker image
5. Health check passes
6. Traffic routes to new version
7. Old version shuts down

**Manual:**

1. Render Dashboard → sentiment-api
2. Click "Manual Deploy" dropdown
3. Select "Deploy latest commit"

**Deployment Time:** ~3-5 minutes

---

## Performance Metrics

Measured on production (Render free tier):

| Metric                | Value                           |
| --------------------- | ------------------------------- |
| Average Response Time | ~250ms                          |
| P95 Response Time     | ~600ms                          |
| Cold Start Time       | ~30 seconds (after 15 min idle) |
| Throughput            | ~15-20 RPS sustained            |
| Error Rate            | < 1%                            |
| Database Query Time   | ~50-100ms avg                   |

**Limitations:**

- Free tier sleeps after 15 min inactivity
- First request after sleep has 30s cold start
- 512MB RAM (suitable for demo, limited for production scale)

---

## Monitoring & Logs

**Real-time Logs:**

- Render Dashboard → sentiment-api → Logs tab
- Shows last 7 days of logs (free tier)

**Metrics:**

- Render Dashboard → sentiment-api → Metrics tab
- CPU usage, memory usage, request count

**Health Monitoring:**

- Automatic health checks every 30 seconds
- Endpoint: `/health`
- Unhealthy containers automatically restarted

---

## Database Backup & Restore

**Automatic Backups:**

- Daily automatic backups (free tier)
- Retained for 7 days
- Location: Render Dashboard → sentiment-db → Backups

**Manual Backup:**

```bash
# Via Render Shell
pg_dump $DATABASE_URL > backup.sql
```

**Restore:**

```bash
# Via Render Shell
psql $DATABASE_URL < backup.sql
```

---

## Troubleshooting

**Issue: Service shows "Unhealthy"**

- Check logs for errors
- Verify `/health` endpoint returns 200
- Ensure DATABASE_URL is set correctly

**Issue: "502 Bad Gateway"**

- Service is deploying or starting up
- Wait 1-2 minutes and retry
- Check Render status page: status.render.com

**Issue: Slow first request**

- Expected behavior on free tier (cold start)
- First request after 15 min idle takes ~30 seconds
- Subsequent requests are fast (~200-300ms)

**Issue: Database connection refused**

- Verify DATABASE_URL uses Internal URL (not External)
- Check PostgreSQL service is running
- Verify network connectivity

---

## Cost Management

**Current Cost:** $0/month (free tier)

**After 90 Days:**

- PostgreSQL expires
- Options:
  1. Migrate to Supabase (free 500MB forever)
  2. Upgrade Render PostgreSQL ($7/month)
  3. Export data and archive project

**To Avoid Unexpected Charges:**

- Set calendar reminder for Day 85 (before expiry)
- Decision required: migrate or upgrade

---

## Security

**HTTPS:** Automatic SSL certificate (Let's Encrypt)
**Secrets:** Stored in Render Environment Variables (encrypted at rest)
**Database:** Not publicly accessible (internal network only)
**API:** Publicly accessible (no authentication — demo project)
**CORS:** Configured for all origins (can be restricted if needed)

---

## Deployment Checklist

Pre-deployment:

- [X] All tests passing locally
- [X] CI pipeline green on GitHub
- [X] Dockerfile builds successfully
- [X] ML model files in repository
- [X] Environment variables documented

Post-deployment:

- [X] Health endpoint returns 200
- [X] Database migrations applied
- [X] 500 records seeded
- [X] All CRUD endpoints tested
- [X] All analytics endpoints tested
- [X] All visualization endpoints tested
- [X] Auto-deployment verified
- [X] Production URL documented
- [X] Monitoring configured

---

## Rollback Procedure

If deployment fails:

1. Render Dashboard → sentiment-api → Deploys tab
2. Find last successful deployment
3. Click "..." → Rollback to this version
4. Render redeploys previous working version

**Rollback time:** ~2-3 minutes

---

## Future Enhancements

**When scaling beyond free tier:**

- Upgrade to Render Standard ($7/month for persistent instances)
- Add Redis for caching (reduce database load)
- Implement rate limiting (prevent abuse)
- Add authentication (API keys or OAuth)
- Set up custom domain
- Enable CORS restrictions
- Add request logging to external service (Datadog, Sentry)

---

## Support

**Render Documentation:** https://render.com/docs
**Render Community:** https://community.render.com
**Render Status:** https://status.render.com
**GitHub Repository:** https://github.com/danyon-satyam/ecp-2024

---

**Deployed by:** Danyon Satyam
**Mentor:** Pramit Dash
**Last Updated:** April 28, 2026
