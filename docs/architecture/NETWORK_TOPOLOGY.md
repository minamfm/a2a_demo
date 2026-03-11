# Network Topology

## Network Architecture

```
Host Machine (localhost)
├── :4000  ─▶  inspector (container :8080)
├── :8001  ─▶  agent1    (container :8000)
├── :8002  ─▶  agent2    (container :8000)
└── :8003  ─▶  agent3    (container :8000)

Docker Bridge Network: a2a-network
┌──────────────────────────────────────────────────────┐
│                                                      │
│  inspector  ──A2A──▶  agent3                        │
│   (internal DNS: inspector:8080)                    │
│                         │                            │
│                    A2A  ├──▶ agent1 (agent1:8000)   │
│                         └──▶ agent2 (agent2:8000)   │
│                                                      │
│  [agent1 may not be on network — see known bug]     │
└──────────────────────────────────────────────────────┘

External
agent1 ──▶ smtp.gmail.com (via gmail.googleapis.com)
agent2 ──▶ sheets.googleapis.com
agent1,2,3 ──▶ generativelanguage.googleapis.com (Gemini)
```

## Port Map

| Service | Host Port | Container Port | Protocol | Purpose |
|---|---|---|---|---|
| inspector | 4000 | 8080 | HTTP | A2A Inspector UI |
| agent1 | 8001 | 8000 | HTTP | Email Agent A2A endpoint |
| agent2 | 8002 | 8000 | HTTP | Sheets Agent A2A endpoint |
| agent3 | 8003 | 8000 | HTTP | Orchestrator A2A endpoint |

## DNS Resolution (Docker)

Inside the `a2a-network`, containers resolve each other by service name:

| Service Name | Resolves To |
|---|---|
| `agent1` | agent1 container IP :8000 |
| `agent2` | agent2 container IP :8000 |
| `agent3` | agent3 container IP :8000 |
| `inspector` | inspector container IP :8080 |

From the host machine, all agents are reachable at `localhost:{host-port}`.

## A2A Discovery Probe Pattern (agent3)

agent3 probes the following URLs at request time:
```
GET http://agent1:8000/.well-known/agent-card.json   timeout=1.0s
GET http://agent2:8000/.well-known/agent-card.json   timeout=1.0s
GET http://agent3:8000/.well-known/agent-card.json   timeout=1.0s
```
Agent3 filters itself from the discovered list by checking `"Orchestrator" in card.name`.

## Traffic Flows

### Browser → Inspector → Orchestrator → Email Agent

```
Browser :browser-port
  └─[HTTP GET /]──▶ inspector :4000
       └─[A2A POST http://agent3:8000]──▶ agent3 :8000
            └─[A2A POST http://agent1:8000]──▶ agent1 :8000
                 └─[HTTPS POST gmail.googleapis.com]──▶ Google Gmail
```

## Network Security

| Control | Status |
|---|---|
| TLS (HTTPS) | Not configured — HTTP only (demo) |
| Network isolation | Docker bridge provides container isolation |
| External access restriction | No firewall rules — all ports bound to 0.0.0.0 |
| mTLS between agents | Not configured |

For production, bind ports to `127.0.0.1` instead of `0.0.0.0`, and add TLS termination (e.g., nginx proxy or Traefik).
