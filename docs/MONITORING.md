# Monitoring & Observability Guide

**Platform:** Render.com Free Tier
**Service:** sentiment-api
**Region:** Frankfurt (EU Central)
**Production URL:** https://sentiment-api-vpmz.onrender.com

---

## 📊 Available Monitoring

### 1. Render Dashboard (Real-time)

**Access:** https://dashboard.render.com/ → sentiment-api

**Built-in Metrics:**

- **Logs:** Real-time streaming, 7-day retention
- **Metrics:** CPU, RAM, request count, response times
- **Health Checks:** Automatic `/health` endpoint monitoring
- **Deploy History:** Track all deployments

**Key Logs to Monitor:**

INFO:     127.0.0.1:50060 - "GET /api/v1/feedback HTTP/1.1" 200 OK
ML model loaded successfully from app/ml/sentiment_model.joblib
INFO  [alembic.runtime.migration] Running upgrade -> abc123

---


### 2. Application Health Check

**Endpoint:** `/health`
**Frequency:** Every 30 seconds (automatic)
**Timeout:** 60 seconds

**Expected Response:**

```json
{
  "status": "ok",
  "app_name": "Student Sentiment Analysis API"
}
```

**Render Actions:**

- ✅ Healthy → Route traffic normally
- ❌ Unhealthy (3 consecutive failures) → Restart container

---


## 🚨 Alert Conditions

**Currently:** No automated alerts (free tier limitation)

**Manual monitoring recommended:**

- Check Render dashboard daily
- Review error logs
- Verify health checks passing

**Future (Paid Tier):**

- Email alerts on service failures
- Webhook notifications to Slack
- Custom alert thresholds

---



## 📈 Performance Baselines

**Established:** May 2, 2026 (Production deployment)

### Normal Operating Metrics

| Endpoint                      | P50    | P95     | P99     |
| ----------------------------- | ------ | ------- | ------- |
| GET /health                   | 150ms  | 320ms   | 450ms   |
| GET /api/v1/feedback          | 200ms  | 650ms   | 900ms   |
| POST /api/v1/feedback         | 250ms  | 850ms   | 1200ms  |
| GET /api/v1/analytics/summary | 350ms  | 1100ms  | 1500ms  |
| GET /api/v1/visualisations/*  | 7000ms | 12000ms | 15000ms |

**Degraded Performance Indicators:**

- P95 response time > 3 seconds (excluding visualizations)
- Error rate > 5%
- CPU usage sustained > 80%
- Memory usage > 480 MB

**Alert Thresholds (Manual Monitoring):**

| Metric            | Warning | Critical |
| ----------------- | ------- | -------- |
| Avg Response Time | >800ms  | >2000ms  |
| Error Rate        | >2%     | >5%      |
| CPU Usage         | >70%    | >90%     |
| Memory Usage      | >400MB  | >480MB   |

---



## ⚠️ Common Issues & Solutions

### Issue 1: Cold Start Timeout

**Symptom:**

504 Gateway Timeout
First request after 15 minutes of inactivity

**Cause:** Render free tier sleeps containers after 15 min idle

**Expected Behavior:** First request takes ~30 seconds

**Solution:**

- For demo: Accept this limitation (communicate to users)
- For production: Upgrade to Render Standard ($7/mo, no sleep)

**Temporary Workaround:**
Create a simple cron job to ping the API every 10 minutes:

```bash
# cron-job.org or similar
*/10 * * * * curl https://sentiment-api-vpmz.onrender.com/health
```

---

### Issue 2: High Visualization Latency

**Symptom:**

GET /api/v1/visualisations/sentiment-bar
Response time: 8-15 seconds


**Cause:** Matplotlib rendering is CPU-intensive on 0.1 vCPU

**Solution:**

1. Reduce chart resolution (quick fix)
2. Add response caching with Redis (1-2 hours)
3. Pre-generate charts on data updates (future)

---

### Issue 3: Rate Limiting (503 errors)

**Symptom:**


**Cause:** Matplotlib rendering is CPU-intensive on 0.1 vCPU

**Solution:**

1. Reduce chart resolution (quick fix)
2. Add response caching with Redis (1-2 hours)
3. Pre-generate charts on data updates (future)

---

### Issue 3: Rate Limiting (503 errors)

**Symptom:**

503 Service Unavailable
Under load (>15 RPS)


**Cause:** Render free tier rate limiting

**Expected Behavior:** 1-3% failure rate at 20+ concurrent users

**Solution:**

- For demo: Limit concurrent test users to <15
- For production: Upgrade to paid tier

---

## 📈 Manual Monitoring Checklist

**Daily:**

- [ ] Check Render dashboard for errors
- [ ] Verify `/health` returns 200
- [ ] Check response time trends

**Weekly:**

- [ ] Review logs for patterns
- [ ] Check database storage (90-day free tier limit approaching?)
- [ ] Verify auto-deploy working

**Before Demo:**

- [ ] Run load test to verify performance
- [ ] Seed database if needed
- [ ] Check all visualization endpoints

---

## 🔍 Debugging Production Issues

### Step 1: Check Render Logs

1. Dashboard → sentiment-api → **Logs** tab
2. Filter by level: `ERROR`, `WARNING`
3. Look for stack traces

**Common Error Patterns:**

```bash
# Database connection failed
sqlalchemy.exc.OperationalError: could not translate host name

# ML model not found
FileNotFoundError: [Errno 2] No such file or directory: 'app/ml/sentiment_model.joblib'

# Memory limit exceeded
exit code 137 (OOMKilled)
```

---

### Step 2: Test Endpoints Manually

```bash
# Health check
curl https://sentiment-api-vpmz.onrender.com/health

# Analytics (should return JSON)
curl https://sentiment-api-vpmz.onrender.com/api/v1/analytics/summary

# Create feedback (should return 201)
curl -X POST https://sentiment-api-vpmz.onrender.com/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "TEST001",
    "gender": "Male",
    "age": 20,
    "study_hours_per_day": 6,
    "attendance_percentage": 85,
    "active_backlogs": 0,
    "academic_feedback": "Good",
    "emotional_feedback": "Happy"
  }'
```

---

### Step 3: Check Database

1. Dashboard → sentiment-db → **Metrics**
2. Verify:
   - Database is running
   - Storage < 1 GB
   - Active connections < 10

---

## 📊 Load Testing Monitoring

When running load tests against production:

1. **Open Render Dashboard** in separate window
2. **Watch Metrics tab** in real-time
3. **Monitor:**

   - CPU usage (should stay <70%)
   - Memory usage (should stay <400MB)
   - Request count spike
4. **After test:**

   - Check logs for errors
   - Review response time distribution
   - Verify no container restarts

---

## ✅ Production Monitoring Status

| Component         | Status            | Notes                |
| ----------------- | ----------------- | -------------------- |
| Health Checks     | ✅ Active         | Automatic every 30s  |
| Application Logs  | ✅ Available      | 7-day retention      |
| Metrics Dashboard | ✅ Available      | CPU, RAM, requests   |
| Error Tracking    | ⚠️ Manual       | Check logs manually  |
| Uptime Monitoring | ⚠️ Manual       | Use external service |
| Alerts            | ❌ Not configured | Free tier limitation |

**Recommendation for Production:**

- External uptime monitoring: UptimeRobot (free)
- Error tracking: Sentry (free tier available)
- Log aggregation: Papertrail (free tier available)

---



## 📊 Production Health Dashboard

**Quick health check URLs:**

```bash
# Health endpoint (should return 200)
curl https://sentiment-api-vpmz.onrender.com/health

# Analytics summary (should return 500 records)
curl https://sentiment-api-vpmz.onrender.com/api/v1/analytics/summary

# Swagger docs (should load)
open https://sentiment-api-vpmz.onrender.com/docs
```


**Expected healthy responses:**

* Health: `{"status": "ok", "app_name": "Student Sentiment Analysis API"}`
* Analytics: `{"sentiment_distribution": {"total": 500, ...}}`
* Docs: HTML page loads


## 🔐 Security Monitoring

**What Render provides (Free Tier):**

* ✅ HTTPS (auto-SSL certificate)
* ✅ Internal database network (not publicly accessible)
* ✅ Environment variable encryption at rest

**What to monitor manually:**

* Unusual request patterns in logs
* High error rates from single IP
* Unexpected database queries

**No DDoS protection on free tier** (upgrade to paid for this)

---



## 📞 Support Resources

**Render Documentation:** https://render.com/docs

**Render Status:** https://status.render.com

**Render Community:** https://community.render.com

**Internal Docs:**

* Architecture: docs/ARCHITECTURE.md
* Performance: docs/PERFORMANCE.md
* Deployment: docs/RENDER_DEPLOYMENT.md

---



**Last Updated:** May 2, 2026

**Monitoring Status:** Active ✅
