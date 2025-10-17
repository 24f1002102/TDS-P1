# Development Guide

## Project Architecture

### Overview
```
┌─────────────┐          ┌──────────────┐         ┌─────────────┐
│  Instructor │          │   Student    │         │   GitHub    │
│             │──task──▶ │     API      │────────▶│   + Pages   │
│  (Round 1)  │          │              │         │             │
└─────────────┘          └──────────────┘         └─────────────┘
       │                        │                        │
       │                        │                        │
       │                   submission                    │
       │                        │                        │
       ▼                        ▼                        │
┌─────────────┐          ┌──────────────┐               │
│ Evaluation  │◀────────│   Database   │               │
│     API     │          │              │               │
└─────────────┘          └──────────────┘               │
       │                                                 │
       │                                                 │
       ▼                                                 │
┌─────────────┐                                         │
│  Evaluate   │────────────────checks──────────────────┘
│   Script    │
└─────────────┘
```

### Components

#### Student Side
1. **API (`student/api.py`)**
   - FastAPI server
   - Receives task requests
   - Validates secret/email
   - Processes in background

2. **LLM Generator (`student/llm_generator.py`)**
   - Integrates with OpenAI/Anthropic
   - Generates complete applications
   - Creates index.html, README.md, LICENSE

3. **GitHub Manager (`student/github_manager.py`)**
   - Creates repositories
   - Pushes code
   - Enables GitHub Pages
   - Updates existing repos (Round 2)

#### Instructor Side
1. **Evaluation API (`instructor/evaluation_api.py`)**
   - FastAPI server
   - Receives repo submissions
   - Validates against tasks
   - Stores in database

2. **Round 1 Script (`instructor/round1.py`)**
   - Reads submissions CSV
   - Generates unique tasks
   - Sends to student endpoints
   - Logs to database

3. **Round 2 Script (`instructor/round2.py`)**
   - Finds Round 1 completions
   - Generates modification tasks
   - Sends to same endpoints

4. **Evaluation Script (`instructor/evaluate.py`)**
   - Fetches repositories
   - Runs static checks (License, README)
   - Runs LLM evaluation (quality)
   - Runs Playwright checks (functionality)
   - Stores results

5. **Task Templates (`instructor/task_templates.py`)**
   - Defines available tasks
   - Generates attachments
   - Parametrizes with seeds

#### Shared
- **Models (`shared/models.py`)**: Pydantic schemas
- **Database (`shared/database.py`)**: SQLAlchemy ORM
- **Config (`shared/config.py`)**: Settings management

## Code Flow

### Student Workflow

```python
# 1. Receive task
POST /api/task
  ↓
# 2. Validate
check_secret() && check_email()
  ↓
# 3. Generate app (background)
LLMGenerator.generate_app(brief, checks, attachments)
  ↓
# 4. Deploy
GitHubManager.create_and_deploy_repo(files)
  ↓
# 5. Submit
submit_with_retry(evaluation_url, submission)
```

### Instructor Workflow

```python
# Round 1
for student in submissions:
    task = generate_task_from_template()
    send_to_student_endpoint(task)
    log_to_database(task)

# Students process and submit

# Evaluation
for repo in submissions:
    results = evaluate_repo(repo)
    store_results(results)

# Round 2
for student in round1_completions:
    task2 = generate_round2_task()
    send_to_student_endpoint(task2)
    log_to_database(task2)
```

## Database Schema

```sql
-- Tasks sent to students
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    email VARCHAR,
    task VARCHAR,
    round INTEGER,
    nonce VARCHAR UNIQUE,
    brief TEXT,
    attachments TEXT,  -- JSON
    checks TEXT,       -- JSON
    evaluation_url VARCHAR,
    endpoint VARCHAR,
    statuscode INTEGER,
    secret VARCHAR
);

-- Student submissions
CREATE TABLE repos (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    email VARCHAR,
    task VARCHAR,
    round INTEGER,
    nonce VARCHAR,
    repo_url VARCHAR,
    commit_sha VARCHAR,
    pages_url VARCHAR
);

-- Evaluation results
CREATE TABLE results (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    email VARCHAR,
    task VARCHAR,
    round INTEGER,
    repo_url VARCHAR,
    commit_sha VARCHAR,
    pages_url VARCHAR,
    check VARCHAR,
    score FLOAT,
    reason TEXT,
    logs TEXT
);
```

## API Contracts

### Task Request (Instructor → Student)
```json
{
  "email": "student@example.com",
  "secret": "secret123",
  "task": "sum-of-sales-a1b2c",
  "round": 1,
  "nonce": "uuid-here",
  "brief": "Create a page that...",
  "checks": ["Check 1", "Check 2"],
  "evaluation_url": "https://eval.com/api/evaluate",
  "attachments": [{"name": "data.csv", "url": "data:..."}]
}
```

### Repo Submission (Student → Evaluation API)
```json
{
  "email": "student@example.com",
  "task": "sum-of-sales-a1b2c",
  "round": 1,
  "nonce": "uuid-here",
  "repo_url": "https://github.com/user/repo",
  "commit_sha": "abc123def456",
  "pages_url": "https://user.github.io/repo/"
}
```

## Adding Features

### New Task Template

1. Edit `instructor/task_templates.py`:
```python
{
    "id": "my-new-task",
    "brief": "Instructions with {seed}",
    "attachments": [
        {"name": "file.txt", "generator": "generate_file"}
    ],
    "checks": [
        "Repo has MIT license",
        "js: document.querySelector('#element') !== null"
    ],
    "round2": [
        {
            "brief": "Add feature X",
            "checks": ["Feature X works"]
        }
    ]
}

def generate_file(seed: str) -> str:
    return f"Content based on {seed}"
```

### New Evaluation Check

1. Edit `instructor/evaluate.py`:
```python
def evaluate_repo(self, repo: Repo, task: Task) -> list[dict]:
    results = []
    
    # Add your check
    result = self.my_custom_check(repo)
    results.append(result)
    
    # ... existing checks
    return results

def my_custom_check(self, repo: Repo) -> dict:
    try:
        # Your logic here
        return {
            "check": "My custom check",
            "score": 1.0,
            "reason": "Passed",
            "logs": ""
        }
    except Exception as e:
        return {
            "check": "My custom check",
            "score": 0.0,
            "reason": str(e),
            "logs": ""
        }
```

### New LLM Provider

1. Edit `student/llm_generator.py`:
```python
def __init__(self):
    if self.provider == "my-provider":
        import my_provider
        self.client = my_provider.Client(api_key=settings.my_api_key)

def _generate_with_my_provider(self, prompt: str) -> dict:
    response = self.client.generate(prompt)
    return parse_response(response)
```

2. Update `shared/config.py`:
```python
my_api_key: Optional[str] = None
llm_provider: str = "openai"  # or "my-provider"
```

## Testing

### Unit Tests
```bash
pytest tests/
```

### Integration Test
```bash
# Terminal 1: Start student API
cd student && python api.py

# Terminal 2: Start evaluation API
cd instructor && python evaluation_api.py

# Terminal 3: Send test task
python scripts/test_student_api.py
```

### Manual Testing
```bash
# Test LLM generation
python -c "
from student.llm_generator import LLMGenerator
gen = LLMGenerator()
files = gen.generate_app(
    'Create hello world page',
    ['Page says Hello'],
    []
)
print(files.keys())
"

# Test GitHub manager
python -c "
from student.github_manager import GitHubManager
gm = GitHubManager()
url, sha, pages = gm.create_and_deploy_repo(
    'test-repo-delete-me',
    {'index.html': '<h1>Test</h1>'}
)
print(f'Repo: {url}')
"
```

## Performance Optimization

### Database
- Use PostgreSQL for production
- Add indexes on email, task, round
- Use connection pooling

### LLM
- Cache common responses
- Use streaming for large outputs
- Implement rate limiting

### Playwright
- Run evaluations in parallel
- Use headed mode only for debugging
- Set reasonable timeouts

## Security Best Practices

1. **Secrets Management**
   - Never commit `.env`
   - Use environment variables
   - Rotate tokens regularly

2. **Input Validation**
   - Validate all API inputs
   - Sanitize file paths
   - Check repo URLs

3. **Rate Limiting**
   - Limit requests per student
   - Prevent spam submissions
   - Timeout long operations

4. **Database**
   - Use parameterized queries
   - Validate foreign keys
   - Backup regularly

## Debugging

### Enable Debug Logging
```python
# In any file
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Database
```bash
# SQLite
sqlite3 tds_project.db
> .tables
> SELECT * FROM tasks LIMIT 5;

# PostgreSQL
psql dbname
> \dt
> SELECT * FROM tasks LIMIT 5;
```

### Playwright Debug
```python
# In .env
HEADLESS=false

# Or in evaluate.py
browser = p.chromium.launch(headless=False, slow_mo=1000)
```

### LLM Debug
```python
# Print prompts
print(prompt)

# Print responses
print(response.choices[0].message.content)
```

## Deployment

### Student API
- Deploy to: Render, Railway, Fly.io
- Keep running 24/7
- Monitor logs
- Auto-restart on failure

### Evaluation API
- Same deployment options
- Ensure database persistence
- Use managed database service
- Set up monitoring

### Production Checklist
- [ ] Use PostgreSQL
- [ ] Set up logging
- [ ] Configure error tracking
- [ ] Enable HTTPS
- [ ] Set environment variables
- [ ] Test end-to-end
- [ ] Monitor resources
- [ ] Set up backups

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

MIT License - See LICENSE file
