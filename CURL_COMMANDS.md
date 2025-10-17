# Quick Curl Commands for Testing Production API

## API Base URL
```
https://tds-student-api-latest.onrender.com
```

---

## 1. Health Check
```bash
curl https://tds-student-api-latest.onrender.com/health
```

**Expected Response:**
```json
{"status":"healthy"}
```

---

## 2. Stats (View Processed Tasks)
```bash
curl https://tds-student-api-latest.onrender.com/stats
```

**Expected Response:**
```json
{
  "status": "ok",
  "total_processed": 0,
  "tasks": []
}
```

---

## 3. Root Endpoint
```bash
curl https://tds-student-api-latest.onrender.com/
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "TDS Student API"
}
```

---

## 4. Submit Task (Round 1) - Simple Test

```bash
curl -X POST https://tds-student-api-latest.onrender.com/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24f1002102@ds.study.iitm.ac.in",
    "secret": "AlanJoanna123#",
    "task": "hello-world-test",
    "round": 1,
    "nonce": "test-nonce-001",
    "brief": "Create a simple HTML page with Hello World in large centered text with a blue background",
    "checks": [
      "Page displays Hello World",
      "Text is centered",
      "Background is blue"
    ],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

**Expected Response:**
```json
{
  "message": "Task received and processing",
  "task": "hello-world-test"
}
```

**Check Results:**
- GitHub Repo: https://github.com/24f1002102/hello-world-test-r1
- GitHub Pages: https://24f1002102.github.io/hello-world-test-r1/

---

## 5. Submit Task - Calculator App

```bash
curl -X POST https://tds-student-api-latest.onrender.com/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24f1002102@ds.study.iitm.ac.in",
    "secret": "AlanJoanna123#",
    "task": "calculator-app",
    "round": 1,
    "nonce": "calc-nonce-001",
    "brief": "Create a simple calculator web app with buttons for digits 0-9 and operations +, -, *, /. Display the result in a centered div",
    "checks": [
      "Page has number buttons 0-9",
      "Page has operation buttons +, -, *, /",
      "Page has equals button",
      "Page displays calculation result",
      "Calculator works correctly"
    ],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

---

## 6. Submit Task - Todo List

```bash
curl -X POST https://tds-student-api-latest.onrender.com/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24f1002102@ds.study.iitm.ac.in",
    "secret": "AlanJoanna123#",
    "task": "todo-list-app",
    "round": 1,
    "nonce": "todo-nonce-001",
    "brief": "Create a todo list web app where users can add tasks, mark them as complete, and delete them. Style it with a modern gradient background",
    "checks": [
      "Can add new tasks",
      "Can mark tasks as complete",
      "Can delete tasks",
      "Has modern gradient styling",
      "Tasks persist in browser"
    ],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

---

## 7. Round 2 - Modify Previous Task

```bash
curl -X POST https://tds-student-api-latest.onrender.com/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24f1002102@ds.study.iitm.ac.in",
    "secret": "AlanJoanna123#",
    "task": "hello-world-test",
    "round": 2,
    "nonce": "test-nonce-002",
    "brief": "Modify the Hello World page to add an animated rainbow gradient background and make the text bounce",
    "checks": [
      "Background has animated rainbow gradient",
      "Text has bouncing animation",
      "Page still displays Hello World"
    ],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

---

## 8. Test with Attachment (Image Data URI)

```bash
curl -X POST https://tds-student-api-latest.onrender.com/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24f1002102@ds.study.iitm.ac.in",
    "secret": "AlanJoanna123#",
    "task": "image-display-app",
    "round": 1,
    "nonce": "image-nonce-001",
    "brief": "Create a page that displays the attached image in the center with a nice border and shadow",
    "checks": [
      "Image is displayed",
      "Image is centered",
      "Image has border and shadow"
    ],
    "attachments": [
      {
        "name": "sample.png",
        "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
      }
    ],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

---

## 9. Test Duplicate Detection

```bash
# Submit the same task again with same nonce
curl -X POST https://tds-student-api-latest.onrender.com/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24f1002102@ds.study.iitm.ac.in",
    "secret": "AlanJoanna123#",
    "task": "hello-world-test",
    "round": 1,
    "nonce": "test-nonce-001",
    "brief": "test",
    "checks": ["test"],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

**Expected Response:**
```json
{
  "message": "Task already processed",
  "task": "hello-world-test"
}
```

---

## 10. Test Invalid Secret

```bash
curl -X POST https://tds-student-api-latest.onrender.com/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24f1002102@ds.study.iitm.ac.in",
    "secret": "wrong-secret",
    "task": "test",
    "round": 1,
    "nonce": "test",
    "brief": "test",
    "checks": ["test"],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

**Expected Response:**
```json
{"detail":"Invalid secret"}
```

---

## 11. Test Invalid Email

```bash
curl -X POST https://tds-student-api-latest.onrender.com/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wrong@email.com",
    "secret": "AlanJoanna123#",
    "task": "test",
    "round": 1,
    "nonce": "test",
    "brief": "test",
    "checks": ["test"],
    "attachments": [],
    "evaluation_url": "https://httpbin.org/post"
  }'
```

**Expected Response:**
```json
{"detail":"Email mismatch"}
```

---

## Running the Full Test Suite

To run all tests automatically:

```bash
./test_production.sh
```

This will:
1. Test all endpoints
2. Submit Round 1 task
3. Wait for processing
4. Submit Round 2 modification
5. Test duplicate detection
6. Show final stats

---

## Monitoring

### Check Stats After Each Submission
```bash
curl https://tds-student-api-latest.onrender.com/stats | jq .
```

### View Render Logs
Go to: https://dashboard.render.com → Select your service → Logs tab

---

## Expected Timeline

- **Task Submission Response**: Immediate (< 1 second)
- **LLM Generation**: 10-30 seconds
- **GitHub Repo Creation**: 5-10 seconds
- **GitHub Pages Deployment**: 30-120 seconds
- **Total Processing Time**: 45-160 seconds per task

---

## Verification Checklist

After submitting a task:

- [ ] API returns 200 with "Task received and processing"
- [ ] Wait 2 minutes
- [ ] Check GitHub for new repo: `https://github.com/24f1002102/{task}-r1`
- [ ] Check GitHub Pages is live: `https://24f1002102.github.io/{task}-r1/`
- [ ] Verify stats endpoint shows task in list
- [ ] Check Render logs for success message

---

## Common Issues

### "Invalid secret"
- Check environment variables on Render
- Ensure STUDENT_SECRET matches exactly

### "Email mismatch"
- Ensure STUDENT_EMAIL is set correctly on Render

### Task not processing
- Check Render logs for errors
- Verify GITHUB_TOKEN is valid
- Verify OPENAI_API_KEY is valid

### GitHub Pages not accessible
- Wait 2-3 minutes (GitHub Pages takes time)
- Check repo settings → Pages section
- Verify branch is set to 'main'
