# AI PR Reviewer - Testing Guide

## Project Overview
This is a **GitHub Pull Request Reviewer** that uses AI (Google Gemini) to automatically review PRs for:
- **Generic Reviews**: Code quality, best practices, security
- **Security Reviews**: Vulnerability detection, authentication, data handling

---

## Architecture

```
GitHub Webhook
    ↓
FastAPI Server (src/main.py)
    ↓
Orchestrator (src/orchestrator.py)
    ├→ MCP Client (fetch PR diff & files)
    ├→ LLM Engine (Google Gemini AI)
    └→ GitHub API (post review comment)
```

---

## How to Test

### 1. **API Health Check** ✅ (No Auth Required)
Test that the server is running:

```bash
curl http://127.0.0.1:8000/
```

Expected response:
```json
{"message": "AI Reviewer is active"}
```

Or visit in browser: **http://127.0.0.1:8000/docs** (Swagger UI)

---

### 2. **Local Webhook Test** (Simulated PR Event)

Create a test file `test_webhook.py`:

```python
import requests
import json

# Simulated GitHub webhook payload
webhook_payload = {
    "action": "opened",
    "pull_request": {
        "id": 1,
        "number": 123,
        "title": "Add new feature",
        "user": {"login": "developer"},
        "body": "This PR adds a new authentication system",
        "head": {
            "sha": "abc123def456"
        }
    },
    "repository": {
        "full_name": "user/repo",
        "name": "repo",
        "url": "https://api.github.com/repos/user/repo"
    }
}

# Send webhook
response = requests.post(
    "http://127.0.0.1:8000/webhook",
    json=webhook_payload,
    headers={
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": "sha256=dummy"  # For testing without GITHUB_WEBHOOK_SECRET
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

Run it:
```bash
python test_webhook.py
```

Expected response:
```json
{"status": "accepted"}
```

---

### 3. **Using the simulate_webhook.py Script**

The project includes a simulation script:

```bash
python scripts/simulate_webhook.py
```

This sends a realistic PR event to your server.

---

### 4. **Real GitHub Webhook Test**

1. **Set up environment variables** in `.env`:
```
GITHUB_TOKEN=ghp_xxxxxxxxxxxx  # GitHub PAT token
GITHUB_WEBHOOK_SECRET=your_secret_key
GOOGLE_API_KEY=your_gemini_api_key
```

2. **Configure GitHub webhook**:
   - Go to repo → Settings → Webhooks
   - Payload URL: `https://your-server.com/webhook`
   - Event: `Pull requests`
   - Secret: Set `GITHUB_WEBHOOK_SECRET`

3. **Create a real PR** on GitHub → Webhook triggers automatically

---

## How Reviews Work

### When a PR is opened/updated:

1. **Webhook Received** → `/webhook` endpoint
2. **Signature Validation** → Verify it's from GitHub
3. **PR Data Extracted** → PR number, title, author, diff
4. **Files Fetched** → Via MCP client (code context)
5. **Persona Selected** → 
   - If "security" keyword found → Security review
   - Else → Generic code review
6. **LLM Analysis** → Google Gemini analyzes the code
7. **Review Posted** → Comment added to PR on GitHub

---

## Expected Outputs

### ✅ Success (You'll see on GitHub PR):

```
🤖 AI Code Review

Security Issues Found: 0
Quality Issues: 2
Suggestions:

1. Consider using type hints in functions
2. Error handling needed for API calls
```

### ❌ Common Issues:

| Error | Cause | Fix |
|-------|-------|-----|
| `JSONDecodeError` | Empty webhook body | Now handled - returns `no_payload` |
| `ModuleNotFoundError: github` | PyGithub not installed | Run `pip install -r requirements.txt` |
| `Missing GITHUB_TOKEN` | Not in .env | Add your GitHub PAT to `.env` |
| `401 Unauthorized` | Bad token | Check token permissions on GitHub |

---

## Configuration Files

- **`.env`** → API keys and secrets
- **`config/personas/`** → Review templates (generic.yaml, security.yaml)
- **`config/policies/`** → Rules for what to flag
- **`src/llm_engine.py`** → LLM configuration & prompts

---

## Key Files to Understand

| File | Purpose |
|------|---------|
| `src/main.py` | FastAPI webhook handler |
| `src/orchestrator.py` | Main workflow coordinator |
| `src/llm_engine.py` | Google Gemini AI integration |
| `src/mcp/client.py` | GitHub API interactions |
| `src/models/review_schema.py` | Review data structure |

---

## Next Steps

1. **Test locally** with `test_webhook.py`
2. **Add `.env`** file with your API keys
3. **Deploy** to cloud (Heroku, AWS, etc.)
4. **Configure** GitHub webhook to your deployed URL
5. **Monitor logs** for issues

---

## Logs to Check

In the terminal where uvicorn is running:

```
INFO:     127.0.0.1:60045 - "POST /webhook HTTP/1.1" 200 OK  ✅ Success
ERROR:    Exception in ASGI application  ❌ Error
```

Monitor these to see real-time PR processing!
