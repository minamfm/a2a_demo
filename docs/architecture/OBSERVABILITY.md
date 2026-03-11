# Observability

## Observability Stack

```
agent1 / agent2 / agent3
  │
  └── print("[DEBUG] ...") → stdout → docker logs
```

No APM, no structured logging, no distributed tracing, no metrics, no alerting.

## Logging

### Pattern Used

All structured debug output uses `print("[DEBUG] ...")` in `agent3/AgentExecutor.py`:

```python
print(f"[DEBUG] Agent 3 execute() started for task_id: {context.task_id}")
print(f"[DEBUG] Router selected target: {selected} (Reasoning: {decision.reasoning})")
print(f"[DEBUG] Failed to reach {url}: {str(e)}")
```

agent1 and agent2 have no explicit logging. Errors surfaces as `Message(parts=[Part(text="Failed...")])`.

### Viewing Logs

```bash
# All containers
docker-compose logs -f

# Specific agent
docker-compose logs -f agent3
docker-compose logs -f agent1
docker-compose logs -f agent2
```

### Key Log Messages (agent3)

| Message Pattern | Meaning |
|---|---|
| `[DEBUG] Agent 3 execute() started for task_id: {id}` | New request received |
| `[DEBUG] Attempting to fetch agent card from {url}` | Discovery probe |
| `[DEBUG] Successfully discovered {name} at {url}` | Agent found |
| `[DEBUG] Failed to reach {url}: {error}` | Agent not reachable |
| `[DEBUG] Router selected target: {url}` | Routing decision made |
| `[DEBUG] Executing tool: {name}` | GenAI tool call (agent2 only) |
| `[DEBUG] Direct response generated.` | No agent matched, LLM answers directly |

## Health Checks

No health check endpoints are configured in `docker-compose.yml` or the Dockerfiles.

**Workaround**: Query the Agent Card endpoint as a proxy health check:

```bash
curl -s http://localhost:8001/.well-known/agent-card.json | jq .name  # "Email Agent"
curl -s http://localhost:8002/.well-known/agent-card.json | jq .name  # "Spreadsheet Agent"
curl -s http://localhost:8003/.well-known/agent-card.json | jq .name  # "Orchestrator Agent"
```

## Debugging Workflow

1. Check containers are running: `docker-compose ps`
2. Check logs: `docker-compose logs -f agent3`
3. Test agent card directly: `curl http://localhost:8001/.well-known/agent-card.json`
4. Use A2A Inspector at `http://localhost:4000`
5. Send raw JSON-RPC: see common issues in `DEPLOYMENT_GUIDE.md`

## Common Failure Signals

| Symptom | Log Pattern | Cause |
|---|---|---|
| agent3 returns empty response | `No agents discovered` | agent1/agent2 containers not reachable (check `netwo:` typo) |
| Email fails silently | `Failed to send email: ...` | token.json missing or expired |
| Sheets fails | `Failed to create spreadsheet: ...` | token.json scope mismatch |
| Routing loop | `Guard: Router selected Orchestrator` | Agent card discovery found agent3 itself |
| LLM calls fail | HTTP 401 from Gemini | `GEMINI_API_KEY` not set correctly |
