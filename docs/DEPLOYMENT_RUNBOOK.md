# Deployment Runbook

**Platform:** Render.com
**Service:** sentiment-api
**Database:** sentiment-db
**Last Deploy:** May 2, 2026

---

## 🚀 Standard Deployment (Automatic)

### Trigger

**Automatic deployment on:**

```bash
git push origin main
```

**Deployment Pipeline:**

1. GitHub webhook notifies Render
2. Render pulls latest code from `main` branch
3. Render builds Docker image (`docker build`)
4. Render runs health checks
5. Render routes traffic to new version (zero downtime)
6. Old version terminated

**Duration:** 3-5 minutes

---

## ✅ Pre-Deployment Checklist

Before pushing to `main`:

- [ ] All tests passing locally (`pytest -v`)
- [ ] Coverage above 80% (`pytest --cov=app --cov-fail-under=80`)
- [ ] CI pipeline green on GitHub Actions
- [ ] Code reviewed (PR approved)
- [ ] Database migrations tested locally
- [ ] No secrets in code (check with `git grep -i 'password\|secret\|api_key'`)
- [ ] Changelog updated (if applicable)

---

## 🔄 Deployment Steps

### Step 1: Merge to Main

```bash
# Ensure develop is up to date
git checkout develop
git pull origin develop

# Merge develop to main
git checkout main
git pull origin main
git merge develop

# Push to main (triggers deployment)
git push origin main
```

---

### Step 2: Monitor Deployment

**Watch build logs:**

1. Go to: https://dashboard.render.com/
2. Click **sentiment-api**
3. Click **Logs** tab
4. Watch for:
   ==> Cloning from [https://github.com/danyon-satyam/ecp-2024](https://github.com/danyon-satyam/ecp-2024)
   ==> Building...
   ==> Deploying...
   ==> Your service is live 🎉

**Expected log sequence:**

[Build Stage]
#1 [internal] load build definition from Dockerfile
#2 [1/10] FROM python:3.11-slim
#3 [2/10] RUN apt-get update && apt-get install...
#4 [5/10] RUN pip install -r requirements.txt
#10 [10/10] RUN mkdir -p app/ml
#11 exporting to docker image format
==> Pushing image to registry...
==> Upload succeeded

[Deploy Stage]
==> Deploying...
==> Setting WEB_CONCURRENCY=1
INFO  [alembic.runtime.migration] Running upgrade -> head
Successfully seeded 500 records (or skipped if exists)
INFO:     Started server process [27]
INFO:     Uvicorn running on [http://0.0.0.0:10000](http://0.0.0.0:10000)
==> Your service is live 🎉

---

### Step 3: Verify Deployment

**Test health endpoint:**

```bash
curl https://sentiment-api-vpmz.onrender.com/health
```

Expected: `{"status": "ok", ...}`

**Test main endpoints:**

```bash
# Analytics (should return 500 records)
curl https://sentiment-api-vpmz.onrender.com/api/v1/analytics/summary

# Swagger UI (should load)
open https://sentiment-api-vpmz.onrender.com/docs
```

**Check Render Metrics:**

1. Dashboard → sentiment-api → **Metrics** tab
2. Verify:
   - CPU usage < 60%
   - Memory usage < 400MB
   - No error spikes

---

## 🚨 Rollback Procedure

**If deployment fails or introduces critical bugs:**

### Quick Rollback (Render Dashboard)

1. Go to: https://dashboard.render.com/
2. Click **sentiment-api**
3. Click **Deploys** tab
4. Find last successful deploy (green checkmark)
5. Click **"..."** → **Redeploy**
6. Confirm

**Duration:** 2-3 minutes

---

### Git Rollback (Manual)

```bash
# Find the last good commit
git log --oneline

# Revert to that commit
git revert <bad-commit-hash>

# Push revert commit (triggers new deploy)
git push origin main
```

---

## 🗄️ Database Migrations

### Running Migrations

**Automatic (on every deploy):**

```dockerfile
CMD alembic upgrade head && ...
```

Migrations run automatically before the server starts.

---

### Manual Migration (if needed)

**Via Render Shell (free tier doesn't have Shell):**

If you upgrade to paid tier:

1. Dashboard → sentiment-api → **Shell** tab
2. Run: `alembic upgrade head`

**Via local connection:**

```bash
# Set DATABASE_URL (from Render dashboard)
export DATABASE_URL="postgresql://..."

# Run migration
alembic upgrade head
```

---

### Creating New Migrations

```bash
# 1. Make changes to app/models/student_feedback.py

# 2. Generate migration
alembic revision --autogenerate -m "add_new_field"

# 3. Review migration file in alembic/versions/

# 4. Test locally
alembic upgrade head

# 5. Commit and deploy
git add alembic/versions/*.py
git commit -m "feat: add new database field"
git push origin main
```

---

## 🔧 Troubleshooting Deployments

### Issue: Build Fails

**Symptom:**

Error: Failed to build image
exit code 1

**Common Causes:**

1. **requirements.txt typo
   Check locally**
   pip install -r requirements.txt
2. **Dockerfile syntax error
   Test locally**
   docker build -t test
3. **Missing file**
   **Verify all files committed**
   git status

**Solution:** Fix error locally, commit, push again

---

### Issue: Deploy Succeeds but Health Check Fails

**Symptom:**

==> Health check failed
==> Container unhealthy

**Check:**

1. **Database connection**
   **Verify DATABASE_URL is set**
   Dashboard → sentiment-api → Environment → DATABASE_URL
2. **Port binding**
   **Check Dockerfile CMD uses ${PORT:-10000}**

   CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
3. **Health endpoint
   Test Locally**
   docker run -p 10000:10000 sentiment-api
   curl localhost:10000/health

---


### Issue: Cold Start Timeout

**Symptom:**

504 Gateway Timeout
(first request after 15 min idle)

**Cause:** Render free tier sleeps containers after 15 min

**Expected Behavior:** First request takes ~30s, subsequent requests fast

**Solutions:**

- **For demo:** Communicate to users (expected behavior)
- **For production:** Upgrade to paid tier ($7/mo, no sleep)
- **Workaround:** Keep-alive ping every 10 minutes

---

### Issue: Database Migration Error

**Symptom:**

alembic.util.exc.CommandError: Can't locate revision

**Cause:** Alembic version mismatch

**Solution:**

```bash
# Reset Alembic to current DB state
alembic stamp head

# Redeploy
git commit --allow-empty -m "fix: reset alembic"
git push origin main
```

---

## 🔐 Environment Variables

**Critical variables (must be set in Render dashboard):**

| Variable      | Value                              | Secret? |
| ------------- | ---------------------------------- | ------- |
| DATABASE_URL  | `postgresql://...`               | ✅ Yes  |
| APP_NAME      | `Student Sentiment Analysis API` | No      |
| DEBUG         | `False`                          | No      |
| API_V1_PREFIX | `/api/v1`                        | No      |

**To update environment variables:**

1. Dashboard → sentiment-api → **Environment** tab
2. Click **Add Environment Variable** or edit existing
3. Click **Save**
4. Service auto-redeploys with new values

---

## 📊 Deployment Metrics

**Track these metrics:**

| Metric              | Target    | Measured   |
| ------------------- | --------- | ---------- |
| Deploy Frequency    | 1-3x/week | Varies     |
| Deploy Duration     | <5 min    | 3-5 min ✅ |
| Deploy Success Rate | >95%      | 100% ✅    |
| Rollback Time       | <5 min    | 2-3 min ✅ |
| Downtime per Deploy | 0 seconds | 0s ✅      |

---

## ✅ Post-Deployment Checklist

After successful deployment:

- [ ] Health check returns 200
- [ ] Swagger UI loads correctly
- [ ] Analytics endpoint returns data
- [ ] Visualization endpoints return PNG images
- [ ] No errors in Render logs (first 5 minutes)
- [ ] CPU usage stabilizes (<60%)
- [ ] Memory usage stable (<400MB)
- [ ] Database record count correct (~500)

---

## 🎯 Deployment Schedule

**Recommended:**

- **Production (main):** Monday/Wednesday only (avoid Fridays!)
- **Time:** 10:00 AM IST (after morning coffee, before lunch)
- **Avoid:** Weekends, late nights, before demos

**For this project:**

- Deploy as needed (demo project, low traffic)
- Communicate deploys to Pramit if during meeting times

---

## 📞 Emergency Contacts

**If deployment emergency:**

- **Render Status:** https://status.render.com
- **Render Support:** https://render.com/docs
- **GitHub Issues:** https://github.com/danyon-satyam/ecp-2024/issues
- **Mentor:** Pramit Dash (pramit@feldstern.com)

---

**Last Updated:** May 2, 2026
**Next Review:** Before major feature deploy
