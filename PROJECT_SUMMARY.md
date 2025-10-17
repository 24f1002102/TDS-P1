# TDS Project 1 - Complete Implementation

## Project Structure

```
TDS-P1/
├── README.md                       # Main project documentation
├── QUICKSTART.md                   # Quick start guide
├── LICENSE                         # MIT License
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
│
├── docs/                           # Documentation
│   ├── STUDENT_GUIDE.md           # Detailed student instructions
│   ├── INSTRUCTOR_GUIDE.md        # Detailed instructor instructions
│   └── DEVELOPMENT.md             # Developer guide
│
├── student/                        # Student-side components
│   ├── __init__.py
│   ├── api.py                     # FastAPI endpoint for receiving tasks
│   ├── llm_generator.py           # LLM integration for app generation
│   └── github_manager.py          # GitHub repo and Pages management
│
├── instructor/                     # Instructor-side components
│   ├── __init__.py
│   ├── evaluation_api.py          # API for receiving submissions
│   ├── round1.py                  # Send initial tasks to students
│   ├── round2.py                  # Send modification tasks
│   ├── evaluate.py                # Evaluate submissions
│   └── task_templates.py          # Task configurations
│
├── shared/                         # Shared utilities
│   ├── __init__.py
│   ├── config.py                  # Configuration management
│   ├── models.py                  # Pydantic models
│   └── database.py                # Database schema and setup
│
├── scripts/                        # Helper scripts
│   ├── setup_student.sh           # Student setup script
│   ├── setup_instructor.sh        # Instructor setup script
│   ├── test_student_api.py        # Test student API
│   └── export_results.py          # Export evaluation results
│
├── examples/                       # Example files
│   ├── sample_task_request.json   # Sample task request
│   └── submissions.csv            # Sample submissions CSV
│
├── run_student.sh                  # Quick start student API
└── run_instructor_api.sh          # Quick start evaluation API
```

## Features Implemented

### ✅ Student Side
- [x] FastAPI endpoint accepting JSON POST requests
- [x] Secret and email validation
- [x] Background task processing
- [x] LLM integration (OpenAI and Anthropic)
- [x] Automatic app generation from briefs
- [x] GitHub repository creation
- [x] GitHub Pages deployment
- [x] Repository updates (Round 2)
- [x] Exponential backoff retry logic
- [x] Error handling and logging

### ✅ Instructor Side
- [x] Evaluation API for receiving submissions
- [x] Database schema (Tasks, Repos, Results)
- [x] Round 1 task generation and sending
- [x] Round 2 task generation and sending
- [x] Three pre-configured task templates:
  - Sum of Sales (CSV processing)
  - Markdown to HTML converter
  - GitHub user info fetcher
- [x] Parametrized tasks with seeds
- [x] Attachment generation (CSV, JSON, Markdown)
- [x] Comprehensive evaluation system:
  - Repository creation time check
  - MIT License verification
  - README.md quality (LLM-based)
  - Code quality (LLM-based)
  - Dynamic Playwright checks
- [x] JavaScript-based checks support
- [x] Results storage and export

### ✅ Documentation
- [x] Main README with overview
- [x] Quick start guide
- [x] Detailed student guide
- [x] Detailed instructor guide
- [x] Development guide
- [x] Setup scripts
- [x] Example files

## Technology Stack

**Backend Framework**
- FastAPI (async Python web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)

**Database**
- SQLAlchemy (ORM)
- SQLite (development) / PostgreSQL (production)

**LLM Integration**
- OpenAI GPT-4 Turbo
- Anthropic Claude 3.5 Sonnet

**GitHub Integration**
- PyGithub (GitHub API client)
- GitPython (Git operations)

**Testing & Automation**
- Playwright (browser automation)
- pytest (testing framework)

**Utilities**
- python-dotenv (environment management)
- httpx/requests (HTTP client)

## Key Design Decisions

### 1. Background Processing
Student API returns 200 immediately and processes tasks in background to avoid timeouts.

### 2. Parametrized Tasks
Tasks use `{seed}` placeholders, generated from `hash(email + timestamp)` for uniqueness and hourly rotation.

### 3. Exponential Backoff
Submission retries use 1, 2, 4, 8, 16 second delays to handle temporary failures.

### 4. Dual LLM Support
Supports both OpenAI and Anthropic APIs for flexibility and fallback options.

### 5. Modular Architecture
Clear separation between student, instructor, and shared components for maintainability.

### 6. Database-Driven Workflow
All state tracked in database (tasks sent, repos submitted, results evaluated).

## Usage Scenarios

### Scenario 1: Student Workflow
1. Student runs API server (`python student/api.py`)
2. Exposes endpoint via ngrok
3. Submits endpoint URL to instructor
4. Receives task request
5. App auto-generated via LLM
6. Repo created and Pages deployed
7. Submission sent to evaluation API
8. (Round 2) Receives modification task
9. Repo updated and redeployed

### Scenario 2: Instructor Workflow
1. Collect student submissions in CSV
2. Deploy evaluation API
3. Run `round1.py` to send tasks
4. Students process and submit
5. Run `evaluate.py` to check submissions
6. Run `round2.py` to send modifications
7. Students update and resubmit
8. Run `evaluate.py` again
9. Export results to CSV

## Database Schema

### Tasks Table
Stores all task requests sent to students.

**Columns**: id, timestamp, email, task, round, nonce, brief, attachments (JSON), checks (JSON), evaluation_url, endpoint, statuscode, secret

### Repos Table
Stores student repository submissions.

**Columns**: id, timestamp, email, task, round, nonce, repo_url, commit_sha, pages_url

### Results Table
Stores evaluation results for each check.

**Columns**: id, timestamp, email, task, round, repo_url, commit_sha, pages_url, check, score, reason, logs

## API Endpoints

### Student API
- `GET /` - Root endpoint (status check)
- `GET /health` - Health check
- `POST /api/task` - Receive task request

### Evaluation API
- `GET /` - Root endpoint (status check)
- `GET /health` - Health check
- `POST /api/evaluate` - Receive repo submission

## Task Templates

### 1. Sum of Sales
**Brief**: Parse CSV, sum sales column, display with Bootstrap

**Round 2 Options**:
- Add product sales table
- Currency conversion with rates JSON
- Region filtering

### 2. Markdown to HTML
**Brief**: Convert Markdown with marked.js and highlight.js

**Round 2 Options**:
- Tabs for HTML/Markdown view
- Load from URL parameter
- Live word count

### 3. GitHub User Created
**Brief**: Fetch GitHub user and display creation date

**Round 2 Options**:
- Status alerts (aria-live)
- Account age calculation
- localStorage caching

## Evaluation Criteria

Each submission evaluated on:

1. **Repository Checks** (Auto)
   - Created after task timestamp
   - MIT License present
   - Public visibility

2. **Static Analysis** (LLM)
   - README.md quality (0-1 score)
   - Code quality (0-1 score)

3. **Dynamic Checks** (Playwright)
   - Page loads successfully
   - Required elements present
   - JavaScript checks pass
   - Task-specific functionality works

## Security Features

- Secret validation on all requests
- Email verification
- Environment variable management
- No secrets in git history (via .gitignore)
- HTTPS for all external communications
- Database input validation
- GitHub token with minimal scopes

## Extensibility

### Adding Task Templates
Edit `instructor/task_templates.py` and add to `TASK_TEMPLATES` list.

### Adding Evaluation Checks
Edit `instructor/evaluate.py` and add methods to `RepoEvaluator` class.

### Supporting New LLM Providers
Edit `student/llm_generator.py` and add provider-specific methods.

### Custom Database
Change `DATABASE_URL` in `.env` to use PostgreSQL, MySQL, etc.

## Testing

### Manual Testing
```bash
# Test student API
python scripts/test_student_api.py

# Test evaluation API
curl http://localhost:8001/health
```

### Integration Testing
Run full workflow with test data in `examples/` directory.

## Deployment Options

### Student API
- ngrok (development)
- Render (production)
- Railway (production)
- Fly.io (production)

### Evaluation API
- Same as student API
- Recommended: Use managed database service

## Limitations & Future Enhancements

### Current Limitations
- SQLite not suitable for concurrent writes (use PostgreSQL)
- LLM generation can be slow (30-60 seconds)
- GitHub Pages deployment delay (5-10 seconds)
- No automatic retry for failed tasks

### Possible Enhancements
- [ ] Add task retry mechanism
- [ ] Implement student dashboard
- [ ] Add real-time progress updates (WebSocket)
- [ ] Support multiple LLM models
- [ ] Add code plagiarism detection
- [ ] Implement grading automation
- [ ] Add student notifications (email/SMS)
- [ ] Support custom task creation UI
- [ ] Add performance metrics dashboard
- [ ] Implement load balancing for evaluation

## Support & Maintenance

### Getting Help
1. Check documentation in `docs/`
2. Review examples in `examples/`
3. Check troubleshooting sections
4. Review error logs
5. Open GitHub issue

### Maintenance Tasks
- Rotate GitHub tokens monthly
- Backup database regularly
- Monitor LLM API usage and costs
- Update dependencies quarterly
- Review and clean old repositories
- Archive completed evaluations

## License

MIT License - See LICENSE file

## Credits

Developed for IITM TDS Project 1 (2025)

## Version

**Version**: 1.0.0  
**Date**: October 17, 2025  
**Status**: Production Ready ✅
