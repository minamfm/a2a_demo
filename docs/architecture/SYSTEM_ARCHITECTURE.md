# System Architecture

## Executive Summary

The A2A Demo is a proof-of-concept system that demonstrates the Agent2Agent (A2A) protocol v0.3.0. It consists of three specialized AI agents and a web inspector, all containerized and communicating via JSON-RPC over HTTP. Agent 3 acts as an orchestrator that dynamically discovers Agents 1 and 2 via their Agent Cards and routes user requests to the appropriate agent based on capability matching.

## C4 Level 1 — System Context

```
┌──────────────────────────────────────────────────────┐
│  User (Browser)                                       │
│      │ HTTP :4000                                     │
│      ▼                                               │
│  ┌─────────────┐       A2A JSON-RPC                  │
│  │  A2A Demo   │◀──────────────────────────────────  │
│  │  System     │                                      │
│  └─────────────┘                                      │
│      │ Gmail API                                      │
│      ├──────────────▶ Google Gmail (external)         │
│      │ Sheets API                                     │
│      └──────────────▶ Google Sheets (external)        │
│      │ Gemini API                                     │
│      └──────────────▶ Google Gemini LLM (external)   │
└──────────────────────────────────────────────────────┘
```

## C4 Level 2 — Container Diagram

```
┌─────────────────────────────────────────────────────────┐
│  a2a-network (Docker bridge)                            │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  inspector (a2aprotocol/inspector:latest) :4000  │   │
│  │  Web UI for testing/inspecting A2A agents        │   │
│  └────────────────────┬─────────────────────────────┘   │
│                       │ A2A JSON-RPC POST                │
│                       ▼                                  │
│  ┌────────────────────────────────────────────────────┐ │
│  │  agent3 (OrchestratorAgentExecutor) :8003          │ │
│  │  LangGraph StateGraph                              │ │
│  │  - Discovers agent1 & agent2 via /.well-known/    │ │
│  │  - Routes via structured LLM output (RouteDecision)│ │
│  │  - Calls downstream via A2A ClientFactory         │ │
│  └──────────────┬──────────────────┬──────────────────┘ │
│                 │ A2A POST          │ A2A POST            │
│                 ▼                  ▼                     │
│  ┌─────────────────────┐ ┌──────────────────────────┐   │
│  │ agent1 :8001        │ │ agent2 :8002              │   │
│  │ EmailAgentExecutor  │ │ SheetsAgentExecutor       │   │
│  │ LangGraph ReAct     │ │ Google GenAI SDK          │   │
│  │ Gmail API (OAuth2)  │ │ Sheets API (OAuth2)       │   │
│  │ Model: gemini-3.1-  │ │ Model: gemini-3.1-        │   │
│  │ flash-lite-preview  │ │ flash-lite-preview        │   │
│  └─────────────────────┘ └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Primary Request Flow — Send Email

```
User → Inspector
     → POST agent3:8000 (A2A message/send)
       agent3: TaskState=working
       agent3: discover_agent_cards() → GET agent1:8000/.well-known/agent-card.json
       agent3: router_node() → LLM → RouteDecision(agent_url="http://agent1:8000")
       agent3: execute_route_node() → call_downstream_agent(agent1:8000)
         → A2A ClientFactory.connect(agent1:8000)
         → POST agent1:8000 (A2A message/send)
           agent1: TaskState=working
           agent1: LangGraph ReAct → send_email(to, subject, body) → Gmail API
           agent1: TaskState=completed → Message(response_text)
       agent3: TaskState=completed → Message(final_response)
User ← Inspector (response shown)
```

## Component Architecture

### agent1 — Email Agent

| File | Role |
|---|---|
| `AgentCard.py` | Declares identity, URL, skills (`send_email`) |
| `AgentExecutor.py` | `EmailAgentExecutor(AgentExecutor)`: LangGraph ReAct loop, Gmail API |
| `main.py` | FastAPI app via `A2AFastAPIApplication`, `InMemoryTaskStore` |

### agent2 — Sheets Agent

| File | Role |
|---|---|
| `AgentCard.py` | Declares identity, URL, skills (`create_spreadsheet`, `append_spreadsheet_values`) |
| `AgentExecutor.py` | `SheetsAgentExecutor(AgentExecutor)`: GenAI SDK manual tool loop, Sheets API |
| `main.py` | FastAPI app via `A2AFastAPIApplication`, `InMemoryTaskStore` |

### agent3 — Orchestrator Agent

| File | Role |
|---|---|
| `AgentCard.py` | Declares identity, URL, skills (`routing`, `coordination`) |
| `AgentExecutor.py` | `OrchestratorAgentExecutor`: LangGraph `StateGraph(AgentState)` with `router` → `executor` nodes |
| `main.py` | FastAPI app via `A2AFastAPIApplication`, `InMemoryTaskStore` |

### langgraph_agent_template

A reference template for adding new LangGraph-based agents. See `langgraph_agent_template/README.md`.

## Technology Stack Matrix

| Component | Package | Version | Purpose |
|---|---|---|---|
| HTTP server | `fastapi` | ≥0.100.0 | ASGI web framework |
| ASGI runtime | `uvicorn` | ≥0.23.0 | Production ASGI runner |
| A2A SDK | `a2a-sdk[http-server]` | latest | A2A protocol types, server, client |
| Agent framework (1,3) | `langgraph` | latest | ReAct agent, StateGraph orchestration |
| LLM client (1,3) | `langchain-google-genai` | latest | Gemini via LangChain |
| GenAI SDK (2) | `google-genai` | latest | Native Gemini client with function calling |
| Google APIs | `google-api-python-client` | latest | Gmail + Sheets REST clients |
| Google Auth | `google-auth-oauthlib` | latest | OAuth 2.0 token management |
| Data validation | `pydantic` | ≥2.0.0 | Type-safe models (RouteDecision, etc.) |
| HTTP client | `httpx` | transitive | Async HTTP for agent discovery + calls |
| LLM model | Gemini | gemini-3.1-flash-lite-preview | Routing, email, sheets decisions |

## Architecture Decision Records

### ADR-001: Separate AgentExecutor per Agent

**Decision**: Each agent has its own `AgentExecutor` class that encapsulates all business logic, decoupled from the A2A server boilerplate.

**Why**: The A2A SDK's `AgentExecutor` interface (`execute`, `cancel`) provides a clean boundary. The server infrastructure (FastAPI, task store, request handler) is reused identically across all agents.

### ADR-002: LangGraph vs GenAI SDK

**Decision**: agent1 and agent3 use LangGraph; agent2 uses the Google GenAI SDK directly.

**Why**: Demonstrates that A2A is framework-agnostic. LangGraph's `create_react_agent` simplifies single-tool loops. The GenAI SDK demonstrates manual multi-turn function calling with `client.chats`.

### ADR-003: Dynamic Agent Discovery

**Decision**: agent3 dynamically discovers agents at startup by polling `/.well-known/agent-card.json` on known service names.

**Why**: Models realistic A2A discovery patterns without a registry. The orchestrator filters out its own card to prevent routing loops.

### ADR-004: InMemoryTaskStore

**Decision**: No persistent task storage.

**Why**: This is a demo. All task state is ephemeral and lost on container restart.

## Cross-Cutting Concerns

| Concern | Approach |
|---|---|
| **Logging** | `print("[DEBUG] ...")` in agent3; no structured logging library |
| **Auth (LLM)** | `GEMINI_API_KEY` env var, read by `langchain-google-genai` and `google-genai` |
| **Auth (Google APIs)** | `token.json` OAuth2 refresh token mounted as Docker volume |
| **Error handling** | agent3 wraps entire execute in try/except; returns error as A2A Message |
| **Configuration** | Environment variables only |
