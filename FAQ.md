# Frequently Asked Questions (FAQ)

## General Questions

### What is this project?
An automated system where students build and deploy web applications using LLMs. The system generates code, creates GitHub repos, deploys to GitHub Pages, and evaluates the results.

### Who is this for?
- **Students**: Learn to build automated deployment systems
- **Instructors**: Automate assignment evaluation at scale

### What technologies does it use?
Python, FastAPI, LLMs (OpenAI/Anthropic), GitHub API, Playwright, SQLite/PostgreSQL

---

## Setup Questions

### Q: How long does setup take?
**A**: About 5-10 minutes for students, 10-15 minutes for instructors.

### Q: Do I need a paid LLM API key?
**A**: Yes, you need either:
- OpenAI API key ($5-10 for typical usage)
- Anthropic API key (similar pricing)

Free tiers exist but may have rate limits.

### Q: Can I use a free GitHub account?
**A**: Yes! You just need a personal access token with `repo` scope.

### Q: What if I don't have ngrok?
**A**: Alternatives:
- cloudflared (Cloudflare tunnel)
- localtunnel
- Deploy to Render/Railway/Fly.io

---

## Student Questions

### Q: What happens when I receive a task?
**A**: Your API:
1. Validates the secret
2. Uses LLM to generate app code
3. Creates a GitHub repo
4. Enables GitHub Pages
5. Submits to evaluation API

All automatically!

### Q: How long does app generation take?
**A**: Usually 30-60 seconds:
- LLM generation: 20-30 seconds
- GitHub operations: 10-20 seconds
- Pages deployment: 5-10 seconds

### Q: What if my API crashes during processing?
**A**: The task is lost. Keep your API running and monitored.

### Q: Can I modify the generated code?
**A**: Yes, but evaluation checks the original commit SHA, so modifications won't affect your score.

### Q: What if GitHub Pages doesn't enable?
**A**: 
1. Check your GitHub token has correct permissions
2. Manually enable Pages in repo settings
3. Select `main` branch, `/` root
4. Update the submission if needed

### Q: How many tasks will I receive?
**A**: Up to 3 tasks, each with 2 rounds (6 total requests).

### Q: What if I miss a task?
**A**: If your API is down, you'll miss it. Keep it running 24/7 or use a cloud deployment.

### Q: Can I use a different LLM?
**A**: Yes, edit `student/llm_generator.py` to add support for your LLM.

### Q: How much will this cost?
**A**: Typical costs:
- OpenAI: $1-3 per task
- Anthropic: Similar
- Total for 6 tasks: $6-20

---

## Instructor Questions

### Q: How do I collect student submissions?
**A**: Create a Google Form with fields:
- Email
- API Endpoint URL
- Secret
Export as CSV.

### Q: Can I send custom tasks?
**A**: Yes! Edit `instructor/task_templates.py` to add your own templates.

### Q: How long does evaluation take?
**A**: Per submission:
- Static checks: 5-10 seconds
- LLM evaluation: 20-30 seconds
- Playwright checks: 10-20 seconds
Total: ~1 minute per submission

### Q: Can I run evaluations in parallel?
**A**: Yes, modify `evaluate.py` to use multiprocessing or asyncio.

### Q: What if a student's Pages URL doesn't work?
**A**: 
- Playwright checks will fail
- Student gets 0 score for dynamic checks
- Manual review may be needed

### Q: Can I re-evaluate a submission?
**A**: Yes, delete the results from the database and run `evaluate.py` again.

### Q: How do I handle late submissions?
**A**: Run Round 1 again with just late students' rows in the CSV.

### Q: Can I see intermediate results?
**A**: Yes, query the database:
```bash
python -c "from shared.database import SessionLocal, Result; db = SessionLocal(); results = db.query(Result).all(); [print(f'{r.email}: {r.check} = {r.score}') for r in results]"
```

### Q: How do I export results?
**A**: Run `python scripts/export_results.py` to generate CSV files.

---

## Technical Questions

### Q: Why FastAPI instead of Flask?
**A**: FastAPI provides:
- Async support for background tasks
- Automatic API documentation
- Built-in validation with Pydantic
- Better performance

### Q: Why SQLite by default?
**A**: Easy setup for development. Use PostgreSQL for production.

### Q: Can I use a different database?
**A**: Yes, change `DATABASE_URL` in `.env`. SQLAlchemy supports PostgreSQL, MySQL, etc.

### Q: Why both OpenAI and Anthropic?
**A**: Provides fallback options if one service has issues.

### Q: How does the seed work?
**A**: Seed = `hash(email + YYYY-MM-DD-HH)[:8]`
- Unique per student per hour
- Ensures different tasks
- Reproducible for debugging

### Q: What's the nonce for?
**A**: Prevents duplicate submissions. Each task has a unique nonce.

### Q: How does Round 2 work?
**A**: 
1. System finds Round 1 repos
2. Generates modification task
3. Student updates existing repo
4. Re-deploys Pages
5. Submits again with Round 2 nonce

### Q: Can students submit multiple times?
**A**: Yes, latest submission overwrites previous ones (same email/task/round/nonce).

---

## Troubleshooting

### Q: Error: "Invalid secret"
**A**: 
- Check `.env` STUDENT_SECRET matches submitted secret
- Verify no extra spaces or quotes

### Q: Error: "GitHub authentication failed"
**A**:
- Verify GITHUB_TOKEN is correct
- Check token has `repo` scope
- Generate new token if expired

### Q: Error: "LLM API error"
**A**:
- Check API key is valid
- Verify you have credits/quota
- Try switching providers

### Q: Error: "Playwright timeout"
**A**:
- Increase TIMEOUT in `.env`
- Check GitHub Pages is actually deployed
- Try with HEADLESS=false to debug

### Q: Error: "Database locked"
**A**:
- SQLite doesn't handle concurrent writes well
- Use PostgreSQL for production
- Or ensure only one process writes at a time

### Q: Student API not receiving requests
**A**:
1. Verify API is running: `curl localhost:8000/health`
2. Check ngrok tunnel is active
3. Verify endpoint URL in submission
4. Check firewall settings

### Q: Generated app doesn't work
**A**:
- LLM sometimes generates incorrect code
- Review the generated code on GitHub
- May need to manually fix
- Consider improving LLM prompt

### Q: GitHub Pages showing 404
**A**:
- Wait 1-2 minutes for deployment
- Check repo settings → Pages is enabled
- Verify branch is `main` and path is `/`
- Check `index.html` exists in repo

---

## Best Practices

### For Students

**✅ Do:**
- Keep API running 24/7
- Use cloud deployment (Render/Railway)
- Monitor logs regularly
- Test with sample requests
- Keep GitHub token secure

**❌ Don't:**
- Commit `.env` to git
- Share your secret
- Turn off API during evaluation period
- Manually modify repos during evaluation
- Use weak secrets

### For Instructors

**✅ Do:**
- Use PostgreSQL for production
- Backup database regularly
- Test with sample submissions first
- Monitor evaluation progress
- Set reasonable deadlines

**❌ Don't:**
- Send tasks without testing
- Use SQLite for >20 students
- Skip database backups
- Hard-code credentials
- Ignore failed evaluations

---

## Advanced Usage

### Q: Can I customize the LLM prompt?
**A**: Yes, edit `student/llm_generator.py` → `_build_prompt()` method.

### Q: Can I add custom checks?
**A**: Yes, edit `instructor/evaluate.py` → `RepoEvaluator` class.

### Q: Can I integrate with other services?
**A**: Yes, the modular architecture makes it easy to add integrations.

### Q: Can I use this for other courses?
**A**: Absolutely! Just create new task templates.

### Q: Can I run this offline?
**A**: No, requires:
- LLM API (internet)
- GitHub API (internet)
- Evaluation API (can be local network)

---

## Performance

### Q: How many students can this handle?
**A**: 
- SQLite: Up to 20 students
- PostgreSQL: 100+ students
- Bottleneck is usually LLM API rate limits

### Q: How can I speed up evaluation?
**A**: 
- Use parallel processing
- Increase timeout values
- Cache LLM responses
- Skip redundant checks

### Q: What are the rate limits?
**A**:
- OpenAI: 3 requests/min (free tier)
- Anthropic: Similar
- GitHub: 5000 requests/hour
Use paid tiers for higher limits.

---

## Security

### Q: Is my GitHub token safe?
**A**: Yes, if you:
- Don't commit `.env`
- Use environment variables
- Rotate tokens regularly
- Use minimal scopes

### Q: Can students cheat?
**A**: Possible attacks:
- Submitting someone else's repo (check commit timestamps)
- Hard-coding answers (LLM evaluation catches this)
- Sharing code (plagiarism detection needed)

### Q: Should I make repos private?
**A**: No, assignment requires public repos for GitHub Pages.

### Q: What data is stored?
**A**: 
- Email addresses
- Repo URLs
- Evaluation scores
- Task details
No passwords or tokens stored.

---

## Costs

### Q: What does this cost to run?
**A**:

**Per Student (6 tasks)**:
- LLM API: $6-20
- GitHub: Free
- Deployment: Free (ngrok) or $5/mo (Render)

**Per Instructor (100 students)**:
- LLM evaluation: $50-100
- Database: Free (SQLite) or $5-25/mo (PostgreSQL)
- Hosting: $5-20/mo

### Q: How can I reduce costs?
**A**:
- Use Anthropic (often cheaper)
- Cache LLM responses
- Use smaller models
- Limit number of rounds
- Share infrastructure costs

---

## Support

### Q: Where can I get help?
**A**:
1. Read documentation in `docs/`
2. Check this FAQ
3. Review error logs
4. Open GitHub issue
5. Contact instructor/maintainer

### Q: How do I report a bug?
**A**: Open a GitHub issue with:
- Error message
- Steps to reproduce
- Logs
- Environment details

### Q: Can I contribute?
**A**: Yes! Fork, make changes, and submit a pull request.

---

## Future Development

### Q: What features are planned?
**A**: See PROJECT_SUMMARY.md for enhancement ideas.

### Q: Will this be maintained?
**A**: As long as the course runs, yes.

### Q: Can I fork this for my own use?
**A**: Yes! MIT License allows it. Just keep attribution.

---

## Still have questions?

Check:
- `README.md` - Project overview
- `docs/STUDENT_GUIDE.md` - Student instructions  
- `docs/INSTRUCTOR_GUIDE.md` - Instructor instructions
- `docs/DEVELOPMENT.md` - Developer guide
- `PROJECT_SUMMARY.md` - Complete feature list

Or open a GitHub issue!
