# 🤖 AI PR Reviewer - Complete Setup & Testing Guide

## ✅ What Just Happened

Your AI PR Reviewer is now **running successfully** at **http://127.0.0.1:8000**

The project is a FastAPI application that:
1. Listens for GitHub webhook events
2. Analyzes pull requests with Google Gemini AI
3. Posts automated code reviews back to GitHub PRs

---

## 🧪 How to Test the Project

### **Option 1: Quick Health Check** (Easiest)
```bash
curl http://127.0.0.1:8000/
```
Expected: `{"message": "AI Reviewer is active"}`

### **Option 2: Interactive API Testing**
Visit in browser: **http://127.0.0.1:8000/docs**
- This opens Swagger UI where you can test endpoints with a nice UI

### **Option 3: Run Local Webhook Test**
```bash
# In a new terminal window (keep uvicorn running)
python test_local.py
```

This script will:
- ✅ Verify server is running
- ✅ Test webhook with empty payload
- ✅ Test webhook with realistic PR data
- ✅ Test webhook with non-PR events (should ignore)

### **Option 4: Manual curl Test**
```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -d '{"action":"opened","pull_request":{"number":42,"title":"Test PR"},"repository":{"full_name":"user/repo"}}'
```

---

## 📊 Understanding the Output

### In the Terminal (where uvicorn is running):

**✅ Good - Request Accepted:**
```
INFO:     127.0.0.1:60045 - "POST /webhook HTTP/1.1" 200 OK
```

**❌ Bad - JSON Error (NOW FIXED):**
Before: `json.decoder.JSONDecodeError: Expecting value`
Now: Returns `{"status": "no_payload", "message": "Empty webhook body"}`

### What Happens After Webhook is Accepted:

1. **Payload parsed** → Extracts PR number, author, title
2. **Repository info fetched** → Gets code context via MCP
3. **Persona selected** → "generic" or "security" review mode
4. **AI analysis runs** → Google Gemini reviews the code
5. **Comment posted** → Review appears on the GitHub PR

---

## 🔧 Configuration Files You Need

### 1. **Create `.env` file** (in the ai-pr-reviewer folder)

Copy from `.env.example`:
```bash
cp .env.example .env
```

Then edit `.env` and add:
```
GITHUB_TOKEN=your_github_pat_token
GOOGLE_API_KEY=your_google_gemini_key
GITHUB_WEBHOOK_SECRET=any_random_secret_you_want
```

**Where to get these:**
- **GITHUB_TOKEN**: https://github.com/settings/tokens → Generate new token (repo scope)
- **GOOGLE_API_KEY**: https://makersuite.google.com/app/apikey → Get free API key
- **GITHUB_WEBHOOK_SECRET**: Make up any string (for security verification)

### 2. **Configuration YAML files** (Already exist)
- `config/personas/generic.yaml` → Generic code review template
- `config/personas/security.yaml` → Security-focused review template
- `config/policies/blocking.yaml` → Critical issues to block
- `config/policies/limits.yaml` → Token/rate limits

---

## 🚀 How to Connect Real GitHub Webhook

### Step 1: Deploy the server (or expose local port)
```bash
# For local testing with ngrok:
ngrok http 8000
# This gives you a public URL like https://xxxx-xx-xxx-xxx.ngrok.io
```

### Step 2: Configure webhook on GitHub
1. Go to your GitHub repo → Settings → Webhooks → Add webhook
2. **Payload URL**: `https://your-server/webhook` (use ngrok URL or deployed URL)
3. **Content type**: `application/json`
4. **Secret**: Same as `GITHUB_WEBHOOK_SECRET` in `.env`
5. **Events**: Pull requests (check ✓)
6. Click Create

### Step 3: Test with real PR
1. Create a pull request on GitHub
2. Check uvicorn logs → Should see processing
3. Check the PR comments → Should have AI review comment

---

## 📁 Project Structure

```
ai-pr-reviewer/
├── src/
│   ├── main.py                    ← FastAPI webhook handler
│   ├── orchestrator.py            ← Main workflow (fetches code, calls LLM)
│   ├── llm_engine.py              ← Google Gemini integration
│   ├── mcp/
│   │   └── client.py              ← GitHub API interactions
│   └── models/
│       └── review_schema.py       ← Data structures
├── config/
│   ├── personas/                  ← Review templates
│   └── policies/                  ← Rules & limits
├── scripts/
│   ├── simulate_webhook.py        ← Simulated webhook
│   └── seed_db.py                 ← Database setup
├── test_local.py                  ← Local testing script ⭐ USE THIS
├── TEST_GUIDE.md                  ← Detailed testing guide ⭐ USE THIS
├── .env.example                   ← Environment template ⭐ COPY & EDIT THIS
├── requirements.txt               ← Python dependencies
└── Dockerfile                     ← For Docker deployment
```

---

## 🐛 Bug Fixed

**What was broken:** 
- Webhook endpoint crashed with `JSONDecodeError` when receiving empty requests

**What I fixed:**
- Added payload validation before parsing JSON
- Returns graceful error responses instead of crashing
- Safely handles malformed requests

**Code change in `src/main.py`:**
```python
# Now checks if payload is empty
if not payload_bytes:
    return {"status": "no_payload", "message": "Empty webhook body"}

# And safely parses JSON
try:
    payload = json.loads(payload_bytes)
except json.JSONDecodeError:
    return {"status": "invalid_json", "message": "Could not parse JSON body"}
```

---

## 🎯 Key Features

✅ **Automatic PR Reviews** - Reviews code when PR is opened/updated  
✅ **Dual Modes** - Generic or Security-focused reviews  
✅ **Context Aware** - Fetches full code context for accurate reviews  
✅ **AI Powered** - Uses Google Gemini for intelligent analysis  
✅ **GitHub Integration** - Posts reviews as PR comments  
✅ **Scalable** - Background tasks prevent webhook timeout  
✅ **Configurable** - Personas and policies in YAML  

---

## 🔍 Monitoring & Logs

### Watch the uvicorn terminal:

```
✅ Success: INFO:     127.0.0.1:60045 - "POST /webhook HTTP/1.1" 200 OK
❌ Error:   ERROR:    Exception in ASGI application
🔄 Processing: Event received: PR #42 opened
```

### Check background processing:
The orchestrator runs in a background task (doesn't block webhook response)
- Logs appear after webhook returns with 200 OK
- Watch for `Orchestrator: Analyzing PR #42...` messages

---

## ⚡ Next Steps

1. **Local Testing** (No config needed):
   ```bash
   python test_local.py
   ```

2. **Production Testing** (Needs config):
   - Create `.env` with API keys
   - Deploy to cloud (Heroku, AWS, GCP, etc.)
   - Configure GitHub webhook

3. **Customize Reviews**:
   - Edit `config/personas/generic.yaml` for review prompt
   - Edit `config/policies/blocking.yaml` for issue severity

---

## 💡 Quick Reference

| Task | Command |
|------|---------|
| Start server | `python -m uvicorn src.main:app --reload` |
| Test locally | `python test_local.py` |
| API docs | Visit http://127.0.0.1:8000/docs |
| Check logs | Watch the uvicorn terminal |
| Copy env template | `cp .env.example .env` |
| View this guide | See `TEST_GUIDE.md` |

---

## ❓ FAQ

**Q: Do I need a GitHub token to test locally?**  
A: No, local testing works without it. You only need it for posting reviews to real PRs.

**Q: Where do the AI reviews appear?**  
A: As comments on the GitHub PR in the "Conversation" tab.

**Q: Can I run this without API keys?**  
A: Yes, locally! Just the webhook validates and returns 200 OK. No actual reviews without keys.

**Q: How long does a review take?**  
A: 5-15 seconds depending on code size and AI response time.

**Q: Can I customize the review criteria?**  
A: Yes! Edit `config/personas/` and `config/policies/` YAML files.

---

## 🎉 You're All Set!

Your AI PR Reviewer is **running and ready to test**! 

**Next move:** Run `python test_local.py` to verify everything works! 🚀
