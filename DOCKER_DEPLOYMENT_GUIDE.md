# 🐳 Docker Deployment Guide

## ✅ Current Status
- Docker image built: `tds-student-api:latest` (~ 2GB)
- Image includes: Python 3.9, FastAPI, Playwright, Chromium
- Ready for local testing and Render deployment

---

## 📋 Step 1: Local Testing (CURRENT)

### Build Image
```bash
cd /Users/arvinsamuela/Desktop/IITM/TDS-P1
docker build -t tds-student-api:latest .
```

### Start Container
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Stats
curl http://localhost:8000/stats

# Root
curl http://localhost:8000/
```

### Test Task Submission
```bash
curl -X POST http://localhost:8000/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24f1002102@ds.study.iitm.ac.in",
    "secret": "AlanJoanna123#",
    "task": "docker-test",
    "round": 1,
    "nonce": "test-123",
    "brief": "Create a simple HTML page",
    "checks": ["Page loads"],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

### Stop Container
```bash
docker-compose down
```

---

## 📦 Step 2: Push to Docker Hub

### 2.1: Create Docker Hub Account
1. Go to https://hub.docker.com
2. Sign up / Log in
3. Create repository: `tds-student-api`
4. Set as **Public** (free tier)

### 2.2: Tag and Push Image
```bash
# Login to Docker Hub
docker login

# Tag image with your username
docker tag tds-student-api:latest YOUR_DOCKERHUB_USERNAME/tds-student-api:latest

# Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/tds-student-api:latest
```

Example:
```bash
docker tag tds-student-api:latest 24f1002102/tds-student-api:latest
docker push 24f1002102/tds-student-api:latest
```

---

## 🚀 Step 3: Deploy to Render

### 3.1: Render Configuration

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Select **"Deploy an existing image from a registry"**

### 3.2: Image Configuration

**Image URL:**
```
docker.io/YOUR_DOCKERHUB_USERNAME/tds-student-api:latest
```

Example:
```
docker.io/24f1002102/tds-student-api:latest
```

**Name:**
```
tds-student-api
```

**Region:**
```
Oregon (US West)
```

**Instance Type:**
```
Free
```

### 3.3: Environment Variables

Add these environment variables on Render:

```
STUDENT_SECRET=AlanJoanna123#
STUDENT_EMAIL=24f1002102@ds.study.iitm.ac.in
GITHUB_TOKEN=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
GITHUB_USERNAME=24f1002102
OPENAI_API_KEY=eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDIxMDJAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.TSOColbPUgcXvMFAW3j1R3iDJOXv2pykKfY2w60apZI
LLM_PROVIDER=openai
API_HOST=0.0.0.0
PYTHONUNBUFFERED=1
PYTHONPATH=/app
```

### 3.4: Advanced Settings

**Health Check Path:**
```
/health
```

**Docker Command:** (Leave blank - uses CMD from Dockerfile)

**Auto-Deploy:** ✅ Yes

### 3.5: Deploy

Click **"Create Web Service"**

Render will:
1. Pull your Docker image from Docker Hub (~2-3 minutes)
2. Start the container
3. Run health checks
4. Make it publicly accessible

---

## 🧪 Step 4: Test Deployed API

Once deployed, Render gives you a URL like:
```
https://tds-student-api.onrender.com
```

### Test Health
```bash
curl https://tds-student-api.onrender.com/health
```

### Test Stats
```bash
curl https://tds-student-api.onrender.com/stats
```

### Test Full Workflow
```bash
curl -X POST https://tds-student-api.onrender.com/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24f1002102@ds.study.iitm.ac.in",
    "secret": "AlanJoanna123#",
    "task": "render-docker-test",
    "round": 1,
    "nonce": "prod-123",
    "brief": "Create a page with Hello from Render Docker",
    "checks": ["Page displays text"],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

---

## 🔄 Step 5: Update & Redeploy

When you make code changes:

### 5.1: Rebuild Image
```bash
docker build -t tds-student-api:latest .
```

### 5.2: Push to Docker Hub
```bash
docker tag tds-student-api:latest YOUR_DOCKERHUB_USERNAME/tds-student-api:latest
docker push YOUR_DOCKERHUB_USERNAME/tds-student-api:latest
```

### 5.3: Trigger Render Redeploy

**Option A: Auto-deploy**
- Render auto-detects new image and redeploys

**Option B: Manual deploy**
- Go to Render dashboard
- Click "Manual Deploy" → "Deploy latest image"

---

## 📊 Monitoring

### View Render Logs
1. Go to Render dashboard
2. Select your service
3. Click "Logs" tab
4. Watch real-time logs

### Check Container Health
```bash
curl https://tds-student-api.onrender.com/health
```

Should return:
```json
{"status":"healthy"}
```

### Check Processed Tasks
```bash
curl https://tds-student-api.onrender.com/stats
```

---

## 🐛 Troubleshooting

### Issue: Image pull fails
**Solution:** Make sure Docker Hub repository is public

### Issue: Container crashes
**Check Render logs for:**
- Missing environment variables
- Import errors
- Memory issues (512 MB limit on free tier)

### Issue: Health check fails
**Check:**
```bash
docker run -p 8000:8000 --env-file .env tds-student-api:latest
```

### Issue: GitHub API fails
**Check:**
- GITHUB_TOKEN is valid
- Token has `repo` scope
- Token hasn't expired

---

## 💡 Tips

### Reduce Image Size
```dockerfile
# Use alpine instead of slim (saves ~500MB)
FROM python:3.9-alpine
```

### View Image Layers
```bash
docker history tds-student-api:latest
```

### Debug Inside Container
```bash
docker run -it tds-student-api:latest /bin/bash
```

### Test with Environment Variables
```bash
docker run -p 8000:8000 \
  -e STUDENT_EMAIL=24f1002102@ds.study.iitm.ac.in \
  -e GITHUB_TOKEN=ghp_... \
  tds-student-api:latest
```

---

## ✅ Deployment Checklist

Before submitting to instructor:

- [ ] Docker image builds successfully
- [ ] Container runs locally without errors
- [ ] Health endpoint returns 200
- [ ] Stats endpoint shows correct data
- [ ] Test task creates GitHub repo
- [ ] GitHub Pages deploys successfully
- [ ] Image pushed to Docker Hub
- [ ] Deployed on Render
- [ ] Render URL is accessible
- [ ] Production task submission works
- [ ] All environment variables set on Render
- [ ] Logs show proper startup messages

---

## 🎯 Final URLs to Submit

```
API Endpoint: https://tds-student-api.onrender.com/api/task
Health Check: https://tds-student-api.onrender.com/health
Stats: https://tds-student-api.onrender.com/stats
GitHub Username: 24f1002102
Docker Hub Image: docker.io/24f1002102/tds-student-api:latest
```

---

## 🚨 Important Notes

1. **Free Tier Limitations:**
   - 512 MB RAM
   - Spins down after 15 min inactivity
   - Cold start takes ~30-60 seconds
   - Use UptimeRobot to keep warm

2. **Docker Hub:**
   - Free tier: 1 private repo + unlimited public repos
   - Must keep image public for Render free tier

3. **Image Size:**
   - Current: ~2 GB (with Playwright + Chromium)
   - This is normal for browser automation
   - Render handles large images well

4. **Secrets:**
   - Never commit `.env` file
   - Set all secrets on Render dashboard
   - Docker Hub image should not contain secrets

---

## 📚 Quick Commands Reference

```bash
# Build
docker build -t tds-student-api:latest .

# Run locally
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Push to Docker Hub
docker login
docker tag tds-student-api:latest YOUR_USER/tds-student-api:latest
docker push YOUR_USER/tds-student-api:latest

# Test locally
curl http://localhost:8000/health

# Test on Render
curl https://tds-student-api.onrender.com/health
```

---

**You're now ready to deploy! 🎉**
