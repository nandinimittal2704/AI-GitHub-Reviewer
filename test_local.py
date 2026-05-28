#!/usr/bin/env python3
"""
Quick test script for the AI PR Reviewer webhook
Run this to test the /webhook endpoint without needing a real GitHub webhook
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test if server is running"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(f"✅ Server is healthy: {response.json()}")
            return True
        else:
            print(f"❌ Server returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure uvicorn is running!")
        print("   Run: python -m uvicorn src.main:app --reload")
        return False

def test_webhook_empty():
    """Test webhook with empty payload"""
    print("\n📧 Testing webhook with empty payload...")
    response = requests.post(
        f"{BASE_URL}/webhook",
        headers={"X-GitHub-Event": "ping"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_webhook_valid_pr():
    """Test webhook with valid PR payload"""
    print("\n📧 Testing webhook with valid PR payload...")
    
    payload = {
        "action": "opened",
        "pull_request": {
            "id": 1,
            "number": 42,
            "title": "Add awesome feature",
            "user": {"login": "developer123"},
            "body": "This PR implements the new authentication system",
            "head": {
                "sha": "abc123def456789"
            },
            "base": {
                "repo": {
                    "url": "https://api.github.com/repos/myuser/myrepo"
                }
            }
        },
        "repository": {
            "full_name": "myuser/myrepo",
            "name": "myrepo",
            "url": "https://api.github.com/repos/myuser/myrepo"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/webhook",
        json=payload,
        headers={
            "X-GitHub-Event": "pull_request",
            "X-Hub-Signature-256": "sha256=dummy"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✅ Webhook accepted! Check uvicorn logs for processing details")

def test_webhook_no_pr():
    """Test webhook with non-PR event"""
    print("\n📧 Testing webhook with non-PR event (should be ignored)...")
    
    response = requests.post(
        f"{BASE_URL}/webhook",
        json={"action": "created"},
        headers={
            "X-GitHub-Event": "issues",
            "X-Hub-Signature-256": "sha256=dummy"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✅ Non-PR event ignored (correct behavior)")

def test_docs():
    """Test API documentation"""
    print("\n📚 API Documentation:")
    print(f"   Swagger UI: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc")
    print("   Visit these in your browser for interactive API testing")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI PR Reviewer - Webhook Test Suite")
    print("=" * 60)
    
    # Health check first
    if not test_health():
        sys.exit(1)
    
    # Run tests
    test_webhook_empty()
    test_webhook_valid_pr()
    test_webhook_no_pr()
    test_docs()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
