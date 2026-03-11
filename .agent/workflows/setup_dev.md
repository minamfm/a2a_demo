---
description: Set up local development environment for a2a_demo — install prerequisites, configure auth, and start containers
---

# Setup Development Environment

## Prerequisites

- Docker Desktop ≥24.0 (running)
- Python 3.x on host (for token generation)
- Git
- `GEMINI_API_KEY` from Google AI Studio (https://aistudio.google.com)
- Google Cloud project with Gmail API and Sheets API enabled
- OAuth2 Desktop Client credentials (`credentials.json`)

## Step 1: Clone and Enter Project
```bash
git clone <repo-url>
cd a2a_demo
```

## Step 2: Create Environment File
```bash
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

## Step 3: Install Python Dependencies (Host — for token generation only)
```bash
pip install google-auth-oauthlib google-api-python-client
```

## Step 4: Generate Google OAuth Token
```bash
python generate_token.py
# Opens browser → log in → approve → saves token.json
```
Requires `credentials.json` at project root.

## Step 5: Fix Known Bug in docker-compose.yml
In `docker-compose.yml`, line 12: change `netwo:` → `networks:`

## Step 6: Build and Start All Containers
// turbo
```bash
docker-compose up -d --build
```

## Step 7: Verify Setup
// turbo
```bash
docker-compose ps
curl -s http://localhost:8001/.well-known/agent-card.json | python -m json.tool
curl -s http://localhost:8002/.well-known/agent-card.json | python -m json.tool
curl -s http://localhost:8003/.well-known/agent-card.json | python -m json.tool
```

## Step 8: Open Inspector
Navigate to http://localhost:4000 in your browser.
Set agent URL to: `http://localhost:8003` (from host) or `http://agent3:8000` (internal).

## Verification Test
Send: `"What is 2 + 2?"` → agent3 should respond directly.
Send: `"Create a spreadsheet called Test"` → should route to agent2.
