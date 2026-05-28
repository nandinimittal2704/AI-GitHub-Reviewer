import os
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from src.orchestrator import process_pr_event

app = FastAPI(title="AI PR Reviewer", version="1.0.0")

# Load Secrets
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

def validate_signature(payload: bytes, signature: str) -> bool:
    if not WEBHOOK_SECRET:
        # If .env is empty, this prints a warning instead of crashing
        print("WARNING: GITHUB_WEBHOOK_SECRET is missing!")
        return False
        
    if not signature:
        return False
        
    expected_signature = "sha256=" + hmac.new(
        key=WEBHOOK_SECRET.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    # Use compare_digest instead of '==' to prevent timing attacks
    return hmac.compare_digest(signature, expected_signature)

@app.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    # We must read raw bytes for the HMAC signature. Parsing to JSON first alters the payload.
    payload_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    
    # Check if payload is empty
    if not payload_bytes:
        return {"status": "no_payload", "message": "Empty webhook body"}
    
    # 1. Validation (Skip if secret is missing for local testing)
    if WEBHOOK_SECRET and not validate_signature(payload_bytes, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse JSON safely
    import json
    try:
        payload = json.loads(payload_bytes)
    except json.JSONDecodeError:
        return {"status": "invalid_json", "message": "Could not parse JSON body"}
    
    event_type = request.headers.get("X-GitHub-Event")

    if event_type == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize","reopened"]:
            print(f"Event received: PR #{payload.get('number')} {action}")
            # Offload to background task to avoid GitHub's 10-second webhook timeout
            background_tasks.add_task(process_pr_event, payload)
    
    return {"status": "accepted"}

@app.get("/")
async def root():
    return {"message": "AI Reviewer is active"}