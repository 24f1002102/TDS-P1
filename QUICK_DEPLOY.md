# 🚀 Quick Docker Test & Deploy

## Current Progress: Building Docker Image... ⏳

---

## ✅ Step 1: Build Complete (When Ready)
Docker will finish building with all dependencies including `gitpython`.

---

## 🧪 Step 2: Test Locally

```bash
# Check container is running
docker ps

# View logs (should see startup message)
docker-compose logs

# Test health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Test stats  
curl http://localhost:8000/stats
# Expected: {"status":"ok","total_processed":0,"tasks":[]}
```

---

## 📦 Step 3: Push to Docker Hub

### 3.1: Login
```bash
docker login
# Enter Docker Hub username and password
```

### 3.2: Tag Image
```bash
# Replace YOUR_USERNAME with your Docker Hub username
docker tag tds-student-api:latest YOUR_USERNAME/tds-student-api:latest
```

Example if your Docker Hub username is `24f1002102`:
```bash
docker tag tds-student-api:latest 24f1002102/tds-student-api:latest
```

### 3.3: Push
```bash
docker push 24f1002102/tds-student-api:latest
```

This will take ~10-15 minutes (uploading 2 GB image).

---

## 🌐 Step 4: Deploy on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Select **"Deploy an existing image from a registry"**
4. Enter image URL:
   ```
   docker.io/24f1002102/tds-student-api:latest
   ```
5. Configure:
   - **Name**: tds-student-api
   - **Region**: Oregon (US West)
   - **Instance Type**: Free

6. Add environment variables (click "Add Environment Variable"):
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

7. Advanced settings:
   - **Health Check Path**: `/health`
   - **Auto-Deploy**: Yes

8. Click **"Create Web Service"**

---

## ✅ Step 5: Test Production

Once deployed, test with Render URL:

```bash
# Replace with your actual Render URL
RENDER_URL="https://tds-student-api.onrender.com"

# Test health
curl $RENDER_URL/health

# Test stats
curl $RENDER_URL/stats

# Test task submission
curl -X POST $RENDER_URL/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24f1002102@ds.study.iitm.ac.in",
    "secret": "AlanJoanna123#",
    "task": "production-test",
    "round": 1,
    "nonce": "test-123",
    "brief": "Create simple HTML page with Hello World",
    "checks": ["Page loads"],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

---

## 📝 What to Submit

```
API Endpoint URL: https://tds-student-api.onrender.com/api/task
Secret: AlanJoanna123#
Student Email: 24f1002102@ds.study.iitm.ac.in
GitHub Username: 24f1002102
GitHub Repo (this project): https://github.com/Arvin-Samuel-A/TDS-P1
Docker Image: docker.io/24f1002102/tds-student-api:latest
```

---

## 🎯 Complete Checklist

- [ ] Docker build successful locally
- [ ] Container runs without errors
- [ ] Health check returns 200
- [ ] Stats endpoint works
- [ ] Test task creates GitHub repo
- [ ] GitHub Pages deploys
- [ ] Pushed to Docker Hub
- [ ] Deployed on Render
- [ ] Production health check passes
- [ ] Production task submission works

---

**Current Status: Waiting for Docker build to complete... ⏳**

Run this to check progress:
```bash
docker-compose logs -f
```
