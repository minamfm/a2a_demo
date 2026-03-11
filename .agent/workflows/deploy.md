---
description: Deploy or restart a2a_demo containers — build, run, verify, rollback
---

# Deploy Workflow

## Deploy All Services (Full Restart)
```bash
docker-compose down
docker-compose up -d --build
```

## Deploy a Single Agent (e.g., after code change)
```bash
docker-compose up -d --build agent3
```

## Verification After Deploy

// turbo
```bash
docker-compose ps
```
All 4 services should show `running`.

// turbo
```bash
curl -s http://localhost:8001/.well-known/agent-card.json | python -m json.tool
curl -s http://localhost:8002/.well-known/agent-card.json | python -m json.tool
curl -s http://localhost:8003/.well-known/agent-card.json | python -m json.tool
```

## Rollback
Since there is no persistent storage, rollback is simply:
```bash
docker-compose down
git checkout <previous-commit-or-tag>
docker-compose up -d --build
```

## Check for Networking Bug First
Before deploying, verify `docker-compose.yml` does NOT have `netwo:` in agent1 config.
```bash
grep -n "netwo" docker-compose.yml
```
If found, fix it: `networks:` then redeploy.

## Post-Deploy Checklist

- [ ] `docker-compose ps` shows all 4 containers running
- [ ] Agent cards return JSON at all 3 ports
- [ ] A2A Inspector loads at http://localhost:4000
- [ ] Test request: `"What is 2+2?"` gets a direct response from agent3
- [ ] Check `docker-compose logs agent3` for any ERROR lines
