# API Reference — a2a_demo

## A2A JSON-RPC Endpoint

**All agents** receive calls at: `POST http://{agent-service}:8000`

Body format: JSON-RPC 2.0 request with `method`, `params`, `id`.

## method: message/send

The only method implemented by all agents.

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "method": "message/send",
  "params": {
    "message": {
      "messageId": "uuid",
      "role": "user",
      "parts": [{ "kind": "text", "text": "Your instruction here" }]
    }
  }
}
```

**Response** (Task):
```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "result": {
    "kind": "task",
    "id": "task-uuid",
    "contextId": "ctx-uuid",
    "status": { "state": "completed" },
    "history": [{ "role": "agent", "parts": [{ "kind": "text", "text": "..." }] }]
  }
}
```

## Agent Cards (GET /.well-known/agent-card.json)

| Agent | URL | Key Skills |
|---|---|---|
| agent1 (Email) | `http://localhost:8001/.well-known/agent-card.json` | `send_email` |
| agent2 (Sheets) | `http://localhost:8002/.well-known/agent-card.json` | `create_spreadsheet`, `append_spreadsheet_values` |
| agent3 (Orchestrator) | `http://localhost:8003/.well-known/agent-card.json` | `routing`, `coordination` |

## Tool Signatures (Internal — not A2A methods)

### agent1 tools (LangChain @tool)
```python
send_email(to_address: str, subject: str, body: str) -> str
```

### agent2 tools (GenAI SDK functions)
```python
create_spreadsheet(title: str) -> str
append_spreadsheet_values(spreadsheet_id: str, range_name: str, values: list[list[str]]) -> str
```

## Error Format
```json
{
  "jsonrpc": "2.0",
  "id": "req-id",
  "error": { "code": -32603, "message": "Internal error" }
}
```

More detail: see `docs/architecture/API_SPECIFICATIONS.md`
