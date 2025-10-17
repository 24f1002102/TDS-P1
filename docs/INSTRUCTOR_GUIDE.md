# Instructor Guide: TDS Project 1

## Setup

### 1. Initial Setup

```bash
# Clone and setup
git clone <repo-url>
cd TDS-P1
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Configure
cp .env.example .env
# Edit .env with instructor credentials
```

### 2. Environment Configuration

```env
# LLM for evaluation
OPENAI_API_KEY=sk-your-key
LLM_PROVIDER=openai

# Database
DATABASE_URL=sqlite:///./tds_project.db
# Or PostgreSQL: postgresql://user:pass@localhost/dbname

# Evaluation API
EVALUATION_API_URL=https://your-domain.com/api/evaluate
EVALUATION_API_HOST=0.0.0.0
EVALUATION_API_PORT=8001

# Playwright
HEADLESS=true
TIMEOUT=15000
```

### 3. Database Initialization

```bash
python -c "from shared.database import init_db; init_db()"
```

## Workflow

### Phase 1: Collect Submissions

#### Create Google Form

Fields:
- Email Address (required)
- API Endpoint URL (required)
- Secret (required)
- GitHub Repository URL (optional)

#### Export Responses

Download as `submissions.csv` with columns:
```
timestamp,email,endpoint,secret
2025-10-17 10:30:00,student@example.com,https://abc.ngrok.io/api/task,secret123
```

### Phase 2: Deploy Evaluation API

#### Option A: Local Development

```bash
cd instructor
python evaluation_api.py
# Runs on http://localhost:8001

# In another terminal, expose with ngrok
ngrok http 8001
# Use the https URL as EVALUATION_API_URL
```

#### Option B: Production Deployment

Deploy `evaluation_api.py` to:
- Render
- Railway  
- Fly.io
- Your own server

Example using Render:
1. Create new Web Service
2. Point to your repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python instructor/evaluation_api.py`

### Phase 3: Send Round 1 Tasks

```bash
cd instructor
python round1.py submissions.csv https://your-eval-api.com/api/evaluate
```

This will:
- ✅ Read all student submissions
- ✅ Generate unique task for each student
- ✅ Send POST request to their endpoint
- ✅ Log task in database
- ✅ Record HTTP status code

### Phase 4: Monitor Submissions

Check database for submissions:

```bash
# Using SQLite
sqlite3 tds_project.db "SELECT email, task, round, repo_url FROM repos ORDER BY timestamp DESC;"

# Using Python
python -c "
from shared.database import SessionLocal, Repo
db = SessionLocal()
repos = db.query(Repo).all()
for r in repos:
    print(f'{r.email}: {r.task} (Round {r.round}) - {r.pages_url}')
"
```

### Phase 5: Evaluate Round 1

```bash
cd instructor
python evaluate.py
```

This will:
- ✅ Fetch each submitted repository
- ✅ Check MIT License
- ✅ Evaluate README quality (LLM)
- ✅ Evaluate code quality (LLM)
- ✅ Run Playwright checks on GitHub Pages
- ✅ Store results in database

### Phase 6: Send Round 2 Tasks

After evaluating Round 1:

```bash
cd instructor
python round2.py
```

This will:
- ✅ Find all Round 1 submissions
- ✅ Generate Round 2 task (modification)
- ✅ Send to student endpoints
- ✅ Log in database

### Phase 7: Evaluate Round 2

```bash
cd instructor
python evaluate.py
```

### Phase 8: Publish Results

Export results:

```bash
# CSV export
python -c "
from shared.database import SessionLocal, Result
import csv

db = SessionLocal()
results = db.query(Result).all()

with open('results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Email', 'Task', 'Round', 'Check', 'Score', 'Reason'])
    for r in results:
        writer.writerow([r.email, r.task, r.round, r.check, r.score, r.reason])
"
```

## Task Templates

### Modifying Existing Templates

Edit `instructor/task_templates.py`:

```python
{
    "id": "sum-of-sales",
    "brief": "Your instructions with {seed} placeholder",
    "attachments": [
        {
            "name": "data.csv",
            "generator": "generate_sales_csv"  # Function name
        }
    ],
    "checks": [
        "Repo has MIT license",
        "README.md is professional",
        # Add more checks
    ],
    "round2": [
        {
            "brief": "Round 2 modification instructions",
            "checks": ["New checks for round 2"]
        }
    ]
}
```

### Adding New Templates

1. Add template to `TASK_TEMPLATES` list
2. Create generator functions if needed:
   ```python
   def generate_your_data(seed: str) -> str:
       """Generate data based on seed."""
       return "your data content"
   ```

### Adding Playwright Checks

In template checks, use `js:` prefix for JavaScript:

```python
"checks": [
    "js: document.title === 'Expected Title'",
    "js: document.querySelector('#element-id') !== null",
    "js: parseFloat(document.querySelector('#total').textContent) > 0"
]
```

## Advanced Features

### Custom Evaluation Logic

Edit `instructor/evaluate.py`:

```python
class RepoEvaluator:
    def custom_check(self, repo: Repo) -> dict:
        """Add your custom check."""
        # Your logic here
        return {
            "check": "Custom check name",
            "score": 1.0,
            "reason": "Check passed",
            "logs": ""
        }
```

### Retry Failed Tasks

```bash
# Find failed tasks
python -c "
from shared.database import SessionLocal, Task

db = SessionLocal()
failed = db.query(Task).filter(Task.statuscode != 200).all()
for t in failed:
    print(f'{t.email}: Status {t.statuscode}')
"

# Retry manually
curl -X POST https://student-endpoint.ngrok.io/api/task \
  -H "Content-Type: application/json" \
  -d @task_data.json
```

### Database Management

#### Backup

```bash
# SQLite
cp tds_project.db tds_project.backup.db

# PostgreSQL
pg_dump dbname > backup.sql
```

#### Reset

```bash
python -c "
from shared.database import Base, engine
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
"
```

## Monitoring

### Check API Status

```bash
curl https://your-eval-api.com/health
# Should return: {"status":"healthy"}
```

### View Logs

```bash
# If running locally
tail -f logs/evaluation_api.log

# If on server
ssh server "tail -f /path/to/logs"
```

### Database Queries

```sql
-- Count submissions by round
SELECT round, COUNT(*) FROM repos GROUP BY round;

-- Average scores by check
SELECT check, AVG(score) FROM results GROUP BY check;

-- Students who completed both rounds
SELECT email FROM repos WHERE round = 1
INTERSECT
SELECT email FROM repos WHERE round = 2;

-- Failed evaluations
SELECT email, task, check, score, reason 
FROM results 
WHERE score < 0.5;
```

## Troubleshooting

### Playwright Issues

```bash
# Reinstall browsers
playwright install chromium --force

# Run in headed mode for debugging
# In .env: HEADLESS=false
```

### LLM API Issues

```bash
# Test OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Switch to Anthropic if needed
# In .env: LLM_PROVIDER=anthropic
```

### Database Issues

```bash
# Check connection
python -c "from shared.database import engine; print(engine.url)"

# Test query
python -c "from shared.database import SessionLocal; db = SessionLocal(); print(db.query('SELECT 1').scalar())"
```

## Grading

### Scoring System

Each check returns a score from 0.0 to 1.0:
- 1.0 = Perfect
- 0.5-0.9 = Partial credit
- 0.0 = Failed

### Calculating Final Grades

```python
from shared.database import SessionLocal, Result

db = SessionLocal()

# Get average score per student per round
results = db.execute("""
    SELECT email, round, AVG(score) as avg_score
    FROM results
    GROUP BY email, round
""").fetchall()

for r in results:
    print(f"{r.email} Round {r.round}: {r.avg_score:.2%}")
```

## Security

1. **Database**: Use PostgreSQL in production, not SQLite
2. **API**: Add authentication to evaluation API
3. **Rate Limiting**: Implement rate limits
4. **HTTPS**: Always use HTTPS for APIs
5. **Secrets**: Never commit database or .env files

## Support

For technical issues:
1. Check logs
2. Verify environment variables
3. Test with sample data
4. Review database state
5. Check Playwright installation
