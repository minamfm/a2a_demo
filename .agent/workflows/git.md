---
description: Git workflow for a2a_demo — branching, commits, and PRs
---

# Git Workflow

## Branch Naming

```
<type>/<short-description>
```

Types: `feature`, `fix`, `chore`, `docs`

Examples:
- `feature/add-calendar-agent`
- `fix/agent1-networking-typo`
- `docs/update-architecture`

## Commit Message Format

```
<type>: <short description in imperative mood, under 72 chars>
```

Examples:
- `fix: correct netwo typo to networks in docker-compose.yml`
- `feat: add agent4 with Google Drive capabilities`
- `chore: update requirements to pin a2a-sdk version`

## Branch and Commit Flow

```bash
# Start new work
git checkout main
git pull
git checkout -b feature/my-feature

# Make changes, then commit
git add .
git commit -m "feat: describe what you did"
git push origin feature/my-feature
```

## Files to Never Commit

Verify `.gitignore` excludes:
```
.env
token.json
credentials.json
__pycache__/
*.pyc
```

## Before Merging

- [ ] All containers start: `docker-compose up -d --build`
- [ ] All agent cards return valid JSON
- [ ] Smoke tests pass (see `/testing` workflow)
- [ ] No hardcoded secrets in source
