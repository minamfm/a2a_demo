---
description: Linting commands for a2a_demo Python code
---

# Linting Workflow

> No linter is currently configured in this project. This workflow documents how to add and run linting.

## Recommended: ruff (fast Python linter)

Install:
```bash
pip install ruff
```

// turbo
Run lint check:
```bash
ruff check agent1/ agent2/ agent3/ langgraph_agent_template/
```

// turbo
Auto-fix:
```bash
ruff check --fix agent1/ agent2/ agent3/ langgraph_agent_template/
```

## Type Checking: mypy

Install:
```bash
pip install mypy
```

// turbo
Run:
```bash
mypy agent1/AgentExecutor.py agent2/AgentExecutor.py agent3/AgentExecutor.py
```

## Format: black

Install:
```bash
pip install black
```

// turbo
Check formatting:
```bash
black --check agent1/ agent2/ agent3/ langgraph_agent_template/
```

Auto-format:
```bash
black agent1/ agent2/ agent3/ langgraph_agent_template/
```
