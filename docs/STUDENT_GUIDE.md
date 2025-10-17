# Student Guide: TDS Project 1

## Quick Start

### 1. Setup

```bash
# Clone and setup
git clone <repo-url>
cd TDS-P1
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your details
```

### 2. Required Configuration

In your `.env` file:

```env
STUDENT_SECRET=create-a-unique-secret-here
STUDENT_EMAIL=your-actual-email@example.com
GITHUB_TOKEN=ghp_your_github_token
GITHUB_USERNAME=your-github-username
OPENAI_API_KEY=sk-your-openai-key
LLM_PROVIDER=openai
```

### 3. Getting a GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (if needed)
4. Copy the token and add to `.env`

### 4. Getting an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy and add to `.env`

Alternatively, use Anthropic:
```env
ANTHROPIC_API_KEY=sk-ant-your-key
LLM_PROVIDER=anthropic
```

### 5. Start Your API

```bash
cd student
python api.py
```

Your server runs at `http://localhost:8000`

### 6. Expose Your Endpoint

#### Option A: ngrok (Recommended)
```bash
# Install ngrok from https://ngrok.com
ngrok http 8000
# Copy the https URL (e.g., https://abc123.ngrok.io)
```

#### Option B: cloudflared
```bash
# Install from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
cloudflared tunnel --url http://localhost:8000
```

#### Option C: Deploy to Cloud
- Deploy to Render, Railway, Fly.io, etc.
- Your endpoint: `https://your-app.render.com/api/task`

### 7. Submit to Instructor

Submit via Google Form:
- **API Endpoint**: `https://your-ngrok-url.ngrok.io/api/task`
- **Secret**: (from your .env)
- **Email**: (from your .env)

### 8. What Happens Next

When the instructor sends a task:

1. ✅ Your API receives the request
2. ✅ Verifies the secret matches
3. ✅ Generates app code using LLM
4. ✅ Creates GitHub repository
5. ✅ Pushes code and enables Pages
6. ✅ Submits to evaluation API
7. ✅ Returns success

### 9. Monitoring

Check your terminal for logs:
```
Processing task: sum-of-sales-a1b2c, round 1
Successfully submitted to evaluation API
Task completed successfully
```

Check GitHub for new repos:
- Named: `task-name-r1` (round 1) or `task-name-r2` (round 2)

### 10. Round 2

When Round 2 request arrives:
- Same endpoint receives it
- Updates existing repo with new features
- Re-deploys Pages
- Submits again

## Troubleshooting

### Error: "Invalid secret"
- Check STUDENT_SECRET in .env matches what you submitted

### Error: "GitHub token invalid"
- Generate new token with `repo` scope
- Update GITHUB_TOKEN in .env

### Error: "LLM API error"
- Check API key is valid
- Ensure you have credits/quota
- Try switching providers (openai ↔ anthropic)

### Error: "Cannot enable GitHub Pages"
- Manually enable Pages in repo settings
- Select `main` branch, `/` root

### Task not processing
- Check API is running
- Check ngrok tunnel is active
- Check logs for errors

## Tips

1. **Keep API Running**: Your API must be running when task requests arrive
2. **Keep Tunnel Active**: ngrok/cloudflared must be active
3. **Monitor Logs**: Watch terminal for processing status
4. **Check GitHub**: Verify repos are created
5. **Test Endpoint**: 
   ```bash
   curl https://your-url.ngrok.io/health
   # Should return: {"status":"healthy"}
   ```

## Advanced

### Custom LLM Prompt

Edit `student/llm_generator.py` to customize how apps are generated.

### Testing Locally

Create `test_request.json`:
```json
{
  "email": "your-email@example.com",
  "secret": "your-secret",
  "task": "test-task",
  "round": 1,
  "nonce": "test-nonce-123",
  "brief": "Create a simple hello world page",
  "checks": ["Page displays 'Hello World'"],
  "evaluation_url": "http://localhost:8001/api/evaluate",
  "attachments": []
}
```

Test:
```bash
curl -X POST http://localhost:8000/api/task \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

## FAQ

**Q: How long does app generation take?**
A: Usually 30-60 seconds for LLM + GitHub operations

**Q: Can I modify generated code?**
A: Yes, but automated evaluation checks the original commit

**Q: What if evaluation fails?**
A: You can manually fix and re-deploy, but timing matters

**Q: How many tasks will I receive?**
A: Up to 3 tasks, each with 2 rounds

**Q: What happens if my API is down?**
A: Instructor may retry, but you might miss the task

## Support

- Check logs first
- Review error messages
- Test with curl
- Verify all credentials
- Ensure services are running
