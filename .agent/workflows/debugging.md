---
description: Debug issues in the a2a_demo system — containers, agents, routing, Google APIs
---

# Debugging Workflow

## Step 1: Check Container Status
// turbo
```bash
docker-compose ps
docker-compose logs --tail=50
```
Expected: all 4 services in `running` state.

## Step 2: Verify Agent Cards (Health Check Proxy)
// turbo
```bash
curl -s http://localhost:8001/.well-known/agent-card.json | python -m json.tool
curl -s http://localhost:8002/.well-known/agent-card.json | python -m json.tool
curl -s http://localhost:8003/.well-known/agent-card.json | python -m json.tool
```
If any returns non-200, the container is unhealthy.

## Step 3: Check agent3 Logs for Discovery
// turbo
```bash
docker-compose logs agent3 | grep DEBUG
```
Look for: `Successfully discovered Email Agent at http://agent1:8000`

## Step 4: Send Test Request via cURL
```bash
curl -X POST http://localhost:8003 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"test-1","method":"message/send","params":{"message":{"messageId":"msg-1","role":"user","parts":[{"kind":"text","text":"What can you do?"}]}}}'
```

## Step 5: Isolate Downstream Agent
Test agent1 and agent2 directly (bypass agent3):
```bash
curl -X POST http://localhost:8001 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"test-2","method":"message/send","params":{"message":{"messageId":"msg-2","role":"user","parts":[{"kind":"text","text":"Send an email to test@example.com saying hello"}]}}}'
```

## Service Dependency Map

| Service | Depends On | Criticality |
|---|---|---|
| agent3 | agent1, agent2 (for routing), Gemini API | High |
| agent1 | Gmail API, Gemini API, token.json | Medium |
| agent2 | Sheets API, Gemini API, token.json | Medium |
| inspector | agent3 | Low (UI only) |

## Common Issues Table

| Symptom | Cause | Fix |
|---|---|---|
| `No agents discovered` in agent3 | agent1 has `netwo:` typo in docker-compose.yml | Fix typo → `networks:`, rebuild |
| `token.json is missing or invalid` | token.json not mounted or expired | Re-run `python generate_token.py` |
| HTTP 401 from Gemini | `GEMINI_API_KEY` not set or wrong | Check `.env`, recreate containers |
| Routing loop (agent selects Orchestrator) | Guard is in place; if repeating, check card names | Verify agent3's card name contains "Orchestrator" |
| agent3 returns `ERROR: ...` | Exception in AgentExecutor | Check `docker-compose logs agent3` for traceback |
| Inspector can't reach agent3 | Using wrong URL format | Use `http://agent3:8000` (internal) or `http://localhost:8003` (host) |

## Log Locations

All logs go to container stdout:
```bash
docker-compose logs -f agent1   # Email agent logs
docker-compose logs -f agent2   # Sheets agent logs
docker-compose logs -f agent3   # Orchestrator + DEBUG routing
docker-compose logs -f inspector
```
