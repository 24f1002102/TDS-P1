# Quick Start Guide

## For Students (5 minutes)

### 1. Setup
```bash
git clone <repo-url>
cd TDS-P1
chmod +x scripts/setup_student.sh
./scripts/setup_student.sh
```

### 2. Configure
Edit `.env`:
```env
STUDENT_SECRET=my-unique-secret
STUDENT_EMAIL=me@example.com
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
GITHUB_USERNAME=myusername
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

### 3. Run
```bash
# Terminal 1: Start API
cd student
python api.py

# Terminal 2: Expose endpoint
ngrok http 8000
```

### 4. Submit
Copy ngrok URL and submit to instructor:
- Endpoint: `https://abc123.ngrok.io/api/task`
- Secret: (from .env)
- Email: (from .env)

### 5. Done!
Wait for task requests. Check GitHub for generated repos.

---

## For Instructors (10 minutes)

### 1. Setup
```bash
git clone <repo-url>
cd TDS-P1
chmod +x scripts/setup_instructor.sh
./scripts/setup_instructor.sh
```

### 2. Configure
Edit `.env`:
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
EVALUATION_API_URL=https://your-eval-api.com/api/evaluate
```

### 3. Deploy Evaluation API
```bash
# Option A: Local + ngrok
cd instructor
python evaluation_api.py &
ngrok http 8001
# Use ngrok URL as EVALUATION_API_URL

# Option B: Deploy to Render/Railway/Fly.io
```

### 4. Collect Submissions
Create `submissions.csv`:
```csv
timestamp,email,endpoint,secret
2025-10-17 10:00:00,student@ex.com,https://abc.ngrok.io/api/task,secret123
```

### 5. Run Round 1
```bash
python instructor/round1.py submissions.csv https://your-eval-api.com/api/evaluate
```

### 6. Evaluate
```bash
python instructor/evaluate.py
```

### 7. Run Round 2
```bash
python instructor/round2.py
python instructor/evaluate.py
```

### 8. Export Results
```bash
python scripts/export_results.py
# Creates: results_export.csv, summary.csv
```

---

## Testing Locally

### Test Student API
```bash
# Edit examples/sample_task_request.json with your email/secret
python scripts/test_student_api.py
```

### Test Evaluation API
```bash
curl -X POST http://localhost:8001/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "task": "test-task",
    "round": 1,
    "nonce": "test-nonce",
    "repo_url": "https://github.com/user/repo",
    "commit_sha": "abc123",
    "pages_url": "https://user.github.io/repo"
  }'
```

---

## Troubleshooting

### Student Side
- **"Invalid secret"** → Check `.env` STUDENT_SECRET matches submission
- **"GitHub error"** → Verify GITHUB_TOKEN has `repo` scope
- **"LLM error"** → Check API key and quota

### Instructor Side
- **"No matching task"** → Verify evaluation API received task from round1.py
- **Playwright fails** → Run `playwright install chromium`
- **Database locked** → Use PostgreSQL instead of SQLite

---

## Resources

- **Student Guide**: `docs/STUDENT_GUIDE.md`
- **Instructor Guide**: `docs/INSTRUCTOR_GUIDE.md`
- **Main README**: `README.md`
- **Examples**: `examples/`
- **Scripts**: `scripts/`
