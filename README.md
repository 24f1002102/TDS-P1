# TDS Project 1: LLM Code Deployment System

An automated system for building, deploying, and evaluating student-generated web applications using Large Language Models (LLMs).

## Overview

This project consists of two main components:

1. **Student Side**: API endpoint that receives task requests, generates applications using LLMs, deploys to GitHub Pages, and submits results
2. **Instructor Side**: Evaluation system that sends tasks, receives submissions, and evaluates them using static analysis, LLMs, and Playwright

## Project Structure

```
TDS-P1/
├── student/                    # Student-side components
│   ├── api.py                 # FastAPI endpoint for receiving tasks
│   ├── llm_generator.py       # LLM integration for app generation
│   └── github_manager.py      # GitHub repo and Pages management
├── instructor/                 # Instructor-side components
│   ├── evaluation_api.py      # API for receiving submissions
│   ├── round1.py              # Send initial tasks
│   ├── round2.py              # Send modification tasks
│   ├── evaluate.py            # Evaluate submissions
│   └── task_templates.py      # Task configurations
├── shared/                     # Shared utilities
│   ├── config.py              # Configuration management
│   ├── models.py              # Pydantic models
│   └── database.py            # Database schema
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## Setup

### Prerequisites

- Python 3.10+
- GitHub Personal Access Token with repo permissions
- OpenAI API key or Anthropic API key
- PostgreSQL (optional, SQLite works for development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd TDS-P1
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers** (for evaluation)
   ```bash
   playwright install chromium
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

### Environment Configuration

Edit `.env` with your credentials:

```env
# Student Configuration
STUDENT_SECRET=your-unique-secret
STUDENT_EMAIL=your-email@example.com

# GitHub
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=your-username

# LLM (choose one)
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=openai  # or anthropic

# Database (optional)
DATABASE_URL=sqlite:///./tds_project.db
```

## Usage

### For Students

#### 1. Start Your API Server

```bash
cd student
python api.py
```

Your API will be available at `http://localhost:8000`

#### 2. Expose Your Endpoint

For development, use a tunneling service:
```bash
# Using ngrok
ngrok http 8000

# Using cloudflared
cloudflared tunnel --url http://localhost:8000
```

#### 3. Submit to Google Form

Submit your:
- API endpoint URL (e.g., `https://your-url.ngrok.io/api/task`)
- Secret (from your `.env`)
- Email

#### 4. Wait for Task Requests

Your API will:
1. Receive the task request
2. Generate the app using LLM
3. Create a GitHub repo
4. Enable GitHub Pages
5. Submit to the evaluation API

### For Instructors

#### 1. Set Up Database

```bash
python -c "from shared.database import init_db; init_db()"
```

#### 2. Start Evaluation API

```bash
cd instructor
python evaluation_api.py
```

#### 3. Send Round 1 Tasks

```bash
python round1.py submissions.csv https://your-eval-api.com/api/evaluate
```

Where `submissions.csv` has columns: `timestamp,email,endpoint,secret`

#### 4. Evaluate Submissions

```bash
python evaluate.py
```

#### 5. Send Round 2 Tasks

```bash
python round2.py
```

#### 6. Final Evaluation

```bash
python evaluate.py
```

## Task Templates

The system includes three pre-configured task templates:

### 1. Sum of Sales
- Parse CSV data
- Display total sales
- Use Bootstrap
- Round 2: Add tables, currency conversion, filtering

### 2. Markdown to HTML
- Convert Markdown to HTML
- Use marked.js and highlight.js
- Round 2: Add tabs, URL loading, word count

### 3. GitHub User Created
- Fetch GitHub user info
- Display account creation date
- Round 2: Add status alerts, age calculation, localStorage caching

## API Endpoints

### Student API

**POST /api/task**
- Receives task requests
- Returns 200 immediately
- Processes in background

### Evaluation API

**POST /api/evaluate**
- Receives repo submissions
- Validates against task database
- Returns 200 on success

## Evaluation Criteria

Each submission is evaluated on:

1. **Repository Checks**
   - Created after task request
   - MIT License present
   - Public repository

2. **Static Analysis**
   - README.md quality (LLM-based)
   - Code quality (LLM-based)
   - No secrets in history

3. **Dynamic Checks** (Playwright)
   - Page loads successfully
   - Required elements present
   - Functionality works as specified
   - Task-specific checks pass

## Database Schema

### Tasks Table
- Tracks all tasks sent to students
- Fields: email, task, round, nonce, brief, checks, etc.

### Repos Table
- Stores student submissions
- Fields: email, task, round, repo_url, commit_sha, pages_url

### Results Table
- Evaluation results for each check
- Fields: email, task, round, check, score, reason, logs

## Troubleshooting

### Student Side

**Issue: GitHub Pages not enabling**
- Solution: Manually enable in repo settings, then re-run

**Issue: LLM API timeout**
- Solution: Increase timeout in `llm_generator.py`

**Issue: Task submission failing**
- Solution: Check evaluation API URL and network connectivity

### Instructor Side

**Issue: Playwright fails**
- Solution: Ensure browsers installed: `playwright install chromium`

**Issue: Database locked**
- Solution: Use PostgreSQL for production instead of SQLite

## Security Considerations

1. **Never commit `.env`** - Keep secrets out of version control
2. **Use environment variables** - Don't hardcode credentials
3. **Validate inputs** - All API endpoints validate requests
4. **Rate limiting** - Consider adding rate limits in production
5. **Secret verification** - Students must provide correct secret

## Development

### Adding New Task Templates

Edit `instructor/task_templates.py`:

```python
{
    "id": "your-task-id",
    "brief": "Task description with {seed}",
    "attachments": [...],
    "checks": [...],
    "round2": [...]
}
```

### Modifying Evaluation Logic

Edit `instructor/evaluate.py` to add custom checks.

## License

MIT License - See LICENSE file

## Support

For issues or questions, please open a GitHub issue.
