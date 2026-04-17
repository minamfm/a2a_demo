# A2A Demo — Architecture Documentation Index

> A demonstration of the Agent2Agent (A2A) protocol v0.3.0: three specialized agents wired together via JSON-RPC over HTTP with dynamic discovery.

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Network: a2a-network          │
│                                                          │
│  ┌───────────┐  A2A    ┌────────────┐  A2A  ┌─────────┐│
│  │ inspector │────────▶│  agent3   │──────▶ │ agent1  ││
│  │ :4000     │ JSON-RPC│ Orchestr. │       │ Email   ││
│  │ (browser) │         │ :8003     │──────▶ │ :8001   ││
│  └───────────┘         └────────────┘  A2A  ├─────────┤│
│                              │               │ agent2  ││
│                              └──────────────▶│ Sheets  ││
│                                              │ :8002   ││
│                                              └─────────┘│
│                                                          │
│  External: Google Gmail API, Google Sheets API           │
│  LLM: Google Gemini (gemini-3.1-flash-lite-preview)     │
└─────────────────────────────────────────────────────────┘
```

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Agent protocol | A2A v0.3.0 | Interoperability between heterogeneous agents |
| Agent framework (1,3) | LangGraph (ReAct) | Tool-calling, structured routing |
| Agent framework (2) | Google GenAI SDK | Direct multi-turn function calling |
| Agent discovery | HTTP GET `/.well-known/agent-card.json` | A2A spec §5.3 well-known URI |
| Task storage | InMemoryTaskStore | Demo; no persistence needed |
| Streaming | Disabled (polling) | Simplicity; `capabilities.streaming: false` |
| Auth | None (demo) | No production secrets beyond GEMINI_API_KEY |

## Documents

| Document | Purpose | Audience |
|---|---|---|
| [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) | C4 diagrams, request flows, tech stack | All |
| [INFRASTRUCTURE.md](INFRASTRUCTURE.md) | Docker setup, env config | Ops, Dev |
| [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md) | Auth, secrets, STRIDE | Security, Dev |
| [DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md) | Task/message data model | Dev |
| [API_SPECIFICATIONS.md](API_SPECIFICATIONS.md) | A2A JSON-RPC endpoints | Dev |
| [OBSERVABILITY.md](OBSERVABILITY.md) | Logging, debugging | Dev, Ops |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Running and troubleshooting | Dev, Ops |
| [NETWORK_TOPOLOGY.md](NETWORK_TOPOLOGY.md) | Ports, DNS, routing | Ops |

## Reading Paths by Role

| Role | Start Here |
|---|---|
| **New Developer** | SYSTEM_ARCHITECTURE → INFRASTRUCTURE → API_SPECIFICATIONS |
| **Adding a New Agent** | SYSTEM_ARCHITECTURE → API_SPECIFICATIONS → DEPLOYMENT_GUIDE |
| **Operations / Debugging** | INFRASTRUCTURE → OBSERVABILITY → NETWORK_TOPOLOGY |
| **A2A Protocol Learner** | API_SPECIFICATIONS → SYSTEM_ARCHITECTURE |

## Core Principle

> All inter-agent communication MUST go through A2A JSON-RPC over HTTP. Agents are opaque to each other — they communicate only via the protocol's data objects (Message, Task, Artifact, Part).
