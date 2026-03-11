# Architecture — a2a_demo

## System Identity

A demo of the **A2A (Agent2Agent) protocol v0.3.0**: three specialized AI agents communicating via JSON-RPC over HTTP with dynamic discovery. No production hardening.

## Service Map

| Service | Path | Host Port | Internal Port | Framework | Purpose |
|---|---|---|---|---|---|
| agent1 | `./agent1` | :8001 | :8000 | LangGraph (ReAct) + FastAPI | Sends emails via Gmail API |
| agent2 | `./agent2` | :8002 | :8000 | Google GenAI SDK + FastAPI | Creates/updates Google Sheets |
| agent3 | `./agent3` | :8003 | :8000 | LangGraph (StateGraph) + FastAPI | Orchestrates routing to agent1/agent2 |
| inspector | N/A (image: `a2aprotocol/inspector:latest`) | :4000 | :8080 | Official A2A Inspector | Browser UI for testing A2A agents |

## Tech Stack

- **Language**: Python 3.11 (in containers)
- **A2A SDK**: `a2a-sdk[http-server]` (v0.3.0 compatible)
- **HTTP Server**: `fastapi` ≥0.100.0 + `uvicorn` ≥0.23.0
- **Agent Frameworks**: `langgraph` (agents 1 and 3), `google-genai` (agent 2)
- **LLM Client**: `langchain-google-genai` (agents 1, 3), `google-genai` (agent 2)
- **LLM Model**: `gemini-3.1-flash-lite-preview` (all agents)
- **Google APIs**: `google-api-python-client` ≥ (Gmail v1, Sheets v4)
- **Auth**: `google-auth-oauthlib` (OAuth2 refresh token)
- **Data validation**: `pydantic` ≥2.0.0
- **Container**: Docker + Docker Compose (bridge network `a2a-network`)

## Docker Network

All containers run on `a2a-network` (Docker bridge). Service names resolve as DNS:
- `agent1:8000`, `agent2:8000`, `agent3:8000`, `inspector:8080`

> **Known Bug**: `docker-compose.yml` agent1 has `netwo:` instead of `networks:` — agent1 may not join the network. Fix the typo before running.

## External Integrations

| Integration | Used By | Auth |
|---|---|---|
| Google Gmail API v1 | agent1 | OAuth2 `token.json` (scope: gmail.send) |
| Google Sheets API v4 | agent2 | OAuth2 `token.json` (scope: spreadsheets) |
| Google Gemini LLM | agent1, agent2, agent3 | `GEMINI_API_KEY` env var |

## Environments

| Env | How | Notes |
|---|---|---|
| Local | `docker-compose up -d --build` | All on localhost |
| Production | Not configured | No K8s/CI/CD |

## Full Architecture Docs

See `docs/architecture/INDEX.md` for complete architecture documentation.
