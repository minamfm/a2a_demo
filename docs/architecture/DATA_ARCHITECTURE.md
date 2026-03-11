# Data Architecture

## Data Store Landscape

```
┌────────────────────────────────────────────────────────────┐
│  a2a_demo Data Stores                                       │
│                                                             │
│  agent1:                    agent2:                         │
│  ┌────────────────────┐    ┌───────────────────────────┐   │
│  │ InMemoryTaskStore  │    │ InMemoryTaskStore          │   │
│  │ (per-request TTL)  │    │ (per-request TTL)          │   │
│  └────────────────────┘    └───────────────────────────┘   │
│                                                             │
│  agent3:                                                    │
│  ┌────────────────────┐                                     │
│  │ InMemoryTaskStore  │                                     │
│  │ (per-request TTL)  │                                     │
│  └────────────────────┘                                     │
│                                                             │
│  External (Google):                                         │
│  ┌──────────────┐   ┌───────────────────┐                  │
│  │ Gmail        │   │ Google Sheets      │                  │
│  │ (write-only) │   │ (create + append)  │                  │
│  └──────────────┘   └───────────────────┘                  │
└────────────────────────────────────────────────────────────┘
```

## Data Store Inventory

| Store | Technology | Purpose | Access Pattern | Pool Config |
|---|---|---|---|---|
| Task store (all agents) | `InMemoryTaskStore` (a2a-sdk) | Holds in-flight task state | In-process, synchronous | N/A — no pool |
| Gmail | Google Gmail API v1 | Deliver outbound emails | Write-only (send) | Per-request HTTP |
| Google Sheets | Google Sheets API v4 | Create and populate spreadsheets | Write (create + append) | Per-request HTTP |

## A2A Data Model

The A2A protocol defines the following core data objects exchanged between agents:

### Task Object

```
Task {
  id: string (UUID, server-generated)
  contextId: string (UUID, groups related tasks)
  status: TaskStatus
  history: Message[]      (conversation turns)
  artifacts: Artifact[]   (generated outputs)
  kind: "task"
}
```

### TaskState Lifecycle

```
submitted → working → input-required → working (loop)
                   └→ completed (terminal)
                   └→ failed    (terminal)
                   └→ canceled  (terminal)
                   └→ rejected  (terminal)
```

Current implementation uses only: `working`, `completed`, `canceled`, `failed`.

### Message Object

```
Message {
  messageId: string (UUID, client-generated)
  contextId: string
  taskId: string
  role: "user" | "agent"
  parts: Part[]
  kind: "message"
}
```

### Part Types

| Type | Used in this project | Description |
|---|---|---|
| `TextPart` | Yes | `{ kind: "text", text: string }` |
| `FilePart` | No | Binary file transfer |
| `DataPart` | No | Structured JSON payload |

## Primary Data Flows

### Email Send Flow (agent1)

```
User text (TextPart)
  → LangGraph messages list: [("user", text)]
  → Gemini extracts: to_address, subject, body
  → send_email() → Gmail API → message_id
  → Response TextPart: "Email sent successfully..."
```

### Sheet Create Flow (agent2)

```
User text
  → GenAI chat.send_message(text)
  → Gemini returns function_calls: [create_spreadsheet(title)]
  → create_spreadsheet() → Sheets API → spreadsheetId
  → chat.send_message([FunctionResponse])
  → Gemini returns text confirmation
  → Response TextPart: "Spreadsheet '...' created. ID: ..."
```

### Orchestration Flow (agent3)

```
User text
  → discover_agent_cards() → [AgentCard, ...]
  → AgentState { input, discovered_agents }
  → router_node: Gemini structured output → RouteDecision
  → execute_route_node: A2A ClientFactory → downstream agent
  → Proxy response back as TextPart
```

## Caching

No caching is implemented. Agent discovery runs on every request in agent3 (timeout: 1.0s per probe).

## Database Change Protocol

No databases. For Google API schema changes, update the tool function signatures in `AgentExecutor.py` of the relevant agent and rebuild the container.
