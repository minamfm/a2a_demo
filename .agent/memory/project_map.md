# Project Map — a2a_demo

## Organizational Pattern: Single-repo, feature-by-agent

```
a2a_demo/
├── agent1/                    # Email Agent (A2A server, LangGraph)
│   ├── AgentCard.py           # A2A identity, skills declaration
│   ├── AgentExecutor.py       # Business logic: Gmail send via LangGraph ReAct
│   ├── main.py                # FastAPI app bootstrap (A2AFastAPIApplication)
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # python:3.11-slim + uvicorn
│
├── agent2/                    # Sheets Agent (A2A server, GenAI SDK)
│   ├── AgentCard.py           # A2A identity, skills declaration
│   ├── AgentExecutor.py       # Business logic: Google Sheets via GenAI function calling
│   ├── main.py                # FastAPI app bootstrap
│   ├── requirements.txt
│   └── Dockerfile
│
├── agent3/                    # Orchestrator Agent (A2A server + client)
│   ├── AgentCard.py           # A2A identity, routing + coordination skills
│   ├── AgentExecutor.py       # Discovery, LangGraph StateGraph routing, A2A client calls
│   ├── main.py                # FastAPI app bootstrap
│   ├── requirements.txt       # Includes a2a-sdk HTTP client
│   └── Dockerfile
│
├── langgraph_agent_template/  # Template for new LangGraph-based A2A agents
│   ├── AgentCard.py           # Minimal agent card template
│   ├── AgentExecutor.py       # Full template with error handling pattern
│   ├── main.py                # Same FastAPI bootstrap pattern
│   ├── requirements.txt
│   ├── Dockerfile             # Adds PYTHONDONTWRITEBYTECODE=1
│   └── README.md
│
├── docs/architecture/         # Architecture documentation (generated)
│   ├── INDEX.md               # Navigation + key decisions
│   ├── SYSTEM_ARCHITECTURE.md # C4 diagrams, tech stack, ADRs
│   ├── API_SPECIFICATIONS.md  # A2A JSON-RPC contracts
│   ├── INFRASTRUCTURE.md      # Docker setup, env config
│   ├── SECURITY_ARCHITECTURE.md # Auth, STRIDE, secrets
│   ├── DATA_ARCHITECTURE.md   # Task/message data model
│   ├── OBSERVABILITY.md       # Logging, debugging
│   ├── DEPLOYMENT_GUIDE.md    # Run, verify, rollback, add agents
│   └── NETWORK_TOPOLOGY.md    # Ports, DNS, traffic flows
│
├── .agent/
│   ├── memory/                # Antigravity project context
│   └── workflows/             # Antigravity slash commands
│
├── docker-compose.yml         # Wires all 4 services (has netwo: bug in agent1)
├── generate_token.py          # OAuth2 token generation helper
├── container_test.py          # Basic container connectivity test
├── README.md                  # Project overview and quickstart
└── .gitignore
```

## Key Files Quick Reference

| File | What to Edit When... |
|---|---|
| `agentX/AgentCard.py` | Changing an agent's identity, URL, or skills |
| `agentX/AgentExecutor.py` | Adding tools, changing LLM logic, fixing bugs |
| `agentX/requirements.txt` | Adding Python dependencies |
| `docker-compose.yml` | Changing ports, env vars, network config |
| `langgraph_agent_template/` | Referenced when scaffolding a new agent |
