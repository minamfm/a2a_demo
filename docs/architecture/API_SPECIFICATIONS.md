# API Specifications

## A2A Protocol Overview

All inter-agent communication uses the **A2A v0.3.0** protocol (JSON-RPC 2.0 over HTTP/HTTPS).

```
Client                           A2A Server
  │                                  │
  │ POST {agent_url}                 │
  │ Content-Type: application/json   │
  │ Body: JSONRPCRequest             │
  │ ─────────────────────────────▶  │
  │                                  │ process task
  │ ◀───────────────────────────── │
  │ Content-Type: application/json  │
  │ Body: JSONRPCResponse           │
```

## Agent Card Endpoints (Discovery)

All three agents expose their Agent Card at the well-known URI per A2A §5.3.

| Agent | URL | Method |
|---|---|---|
| agent1 | `http://agent1:8000/.well-known/agent-card.json` | GET (unauthenticated) |
| agent2 | `http://agent2:8000/.well-known/agent-card.json` | GET (unauthenticated) |
| agent3 | `http://agent3:8000/.well-known/agent-card.json` | GET (unauthenticated) |

**Response shape** (A2A AgentCard):
```json
{
  "id": "agent1-email",
  "name": "Email Agent",
  "description": "Agent that sends emails via Gmail API.",
  "version": "1.0.0",
  "url": "http://agent1:8000",
  "capabilities": { "streaming": false },
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "skills": [
    {
      "id": "send_email",
      "name": "Send Email",
      "description": "Capable of sending emails to any address with a custom subject and body.",
      "tags": ["email", "communication"],
      "examples": ["Send an email to john@example.com saying hi"]
    }
  ]
}
```

## A2A RPC Methods (Implemented)

### `message/send`

**Used by**: Inspector → agent3, agent3 → agent1, agent3 → agent2

**Request** (JSON-RPC 2.0):
```json
{
  "jsonrpc": "2.0",
  "id": "req-uuid",
  "method": "message/send",
  "params": {
    "message": {
      "messageId": "msg-uuid",
      "role": "user",
      "parts": [
        { "kind": "text", "text": "Send an email to alice@example.com saying hello" }
      ]
    }
  }
}
```

**Response** (Task or Message):
```json
{
  "jsonrpc": "2.0",
  "id": "req-uuid",
  "result": {
    "kind": "task",
    "id": "task-uuid",
    "contextId": "ctx-uuid",
    "status": { "state": "completed" },
    "history": [
      {
        "role": "agent",
        "parts": [{ "kind": "text", "text": "Email sent successfully to alice@example.com." }]
      }
    ]
  }
}
```

### `tasks/get`

Retrieve current state of a task by ID. Used for polling after `message/send`.

```
method: "tasks/get"
params: { "id": "task-uuid" }
response: Task object
```

### `tasks/cancel`

Cancel an in-progress task.

```
method: "tasks/cancel"
params: { "id": "task-uuid" }
```

> **Note**: Streaming (`message/stream`) is declared as `false` in all three Agent Cards. The agents do NOT implement SSE streaming. The `capabilities.streaming: false` field communicates this to clients per A2A §5.5.

## Agent-Specific RPC Interfaces

### agent1 — `message/send` with send_email tool

The LangGraph ReAct agent interprets the user text and calls:
```
send_email(to_address: str, subject: str, body: str) -> str
```
Returns `"Email sent successfully to {to_address}. Message ID: {id}"`.

### agent2 — `message/send` with sheets tools

The GenAI SDK agent can call either:
```
create_spreadsheet(title: str) -> str
append_spreadsheet_values(spreadsheet_id: str, range_name: str, values: list[list[str]]) -> str
```

### agent3 — `message/send` (routing)

Accepts user text → runs LangGraph router → calls downstream agent → proxies response.
The `RouteDecision` structured output:
```python
class RouteDecision(BaseModel):
    agent_url: str   # must be a discovered agent URL, or "direct_response"
    reasoning: str
```

## Error Codes

| Code | Name | Meaning |
|---|---|---|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid request | Not a valid JSON-RPC object |
| -32601 | Method not found | Unknown method (e.g. `tasks/foo`) |
| -32602 | Invalid params | Wrong params structure |
| -32603 | Internal error | Server-side exception |
| -32001 | TaskNotFoundError | Task ID doesn't exist |
| -32002 | TaskNotCancelableError | Task already in terminal state |
| -32004 | UnsupportedOperationError | Feature not supported |

## API Versioning

No API versioning. The A2A SDK version is `a2a-sdk[http-server]` (latest). All three agents are locked to A2A v0.3.0 spec behavior via the SDK.

## Inspector UI

| URL | Description |
|---|---|
| `http://localhost:4000` | A2A Inspector web UI (official `a2aprotocol/inspector:latest` image) |

Connect the Inspector to: `http://agent3:8000` (inside Docker) or `http://localhost:8003` (from host).
