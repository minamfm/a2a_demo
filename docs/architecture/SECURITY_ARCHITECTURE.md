# Security Architecture

## Security Layers

```
External
  │ HTTPS (not configured — HTTP only in this demo)
  ▼
Docker Network (a2a-network — bridge, no TLS)
  │
  ├── A2A JSON-RPC (no auth headers in this demo)
  │
  ├── Gemini API (GEMINI_API_KEY env var)
  │
  └── Google APIs (OAuth2 token.json — pre-authorized)
```

## Authentication Mechanisms

### LLM Authentication (Google Gemini)

| Mechanism | How | Services |
|---|---|---|
| API Key | `GEMINI_API_KEY` environment variable | agent1, agent2, agent3 |

The key is passed via `docker-compose.yml` environment block and picked up automatically by the `langchain-google-genai` and `google-genai` SDKs. The key is NOT stored in source code.

### Google Workspace Authentication

| Mechanism | How | Services |
|---|---|---|
| OAuth 2.0 (offline) | `token.json` mounted as volume at `/app/token.json` | agent1, agent2 |

Scopes:
- agent1: `https://www.googleapis.com/auth/gmail.send`
- agent2: `https://www.googleapis.com/auth/spreadsheets`

Token auto-refresh: handled by `google-auth` library — if `creds.expired` and `creds.refresh_token` exists, it calls `creds.refresh(Request())`. If refresh fails, an exception is raised.

### A2A Inter-Agent Authentication

**Current state**: None. The `AgentCard.capabilities` objects do not declare any authentication scheme. All A2A calls are unauthenticated HTTP within the Docker bridge network.

**A2A §4 guidance**: Production deployments should add an `authentication` field to the AgentCard defining schemes (e.g., Bearer token, mTLS).

## STRIDE Threat Model

| Threat | Attack Surface | Current Mitigation | Gap |
|---|---|---|---|
| **Spoofing** | Agent card discovery | Docker DNS (service names) | No agent authentication |
| **Tampering** | JSON-RPC message body | None | No payload signing or mTLS |
| **Repudiation** | Task execution | None | No audit log |
| **Information Disclosure** | token.json in container | Volume mount (not baked into image) | token.json exposed if container filesystem is read |
| **DoS** | agent3 discovery loop | 1.0s timeout per agent probe | Orchestrator re-discovers on every request |
| **Elevation** | Gmail send scope | Minimal OAuth scope | token.json grants send access to the entire inbox account |

## Secrets Architecture

| Secret | Where Stored | How Injected | Rotation |
|---|---|---|---|
| `GEMINI_API_KEY` | Host `.env` file | Docker Compose env block | Manual — update `.env`, recreate containers |
| `token.json` | Host filesystem | Bind mount volume | Re-run `generate_token.py` |
| `credentials.json` | Host filesystem | Manual copy (not mounted to containers) | From Google Cloud Console |

> **Do NOT commit** `token.json`, `credentials.json`, or `.env` to Git. Verify `.gitignore` covers these.

## Container Security

| Agent | Root User | Security Context | Read-Only FS |
|---|---|---|---|
| agent1 | Yes (default) | None configured | No |
| agent2 | Yes (default) | None configured | No |
| agent3 | Yes (default) | None configured | No |

**Improvement**: Add `USER 1000` to Dockerfiles and set `read_only: true` in Compose for production.

## Input Validation

The A2A SDK validates `Message`, `Part`, and `Task` shapes via Pydantic v2 models. Business-logic inputs (email address, spreadsheet ID) are passed directly to Google API client libraries without additional validation — injection attacks are mitigated by the Gmail/Sheets API itself.

## Security of Agent Cards

Agent Cards in this demo are public (no auth required to fetch). This is acceptable for a demo but violates A2A §5.4 if the card contains sensitive information. Current cards do not contain secrets.
