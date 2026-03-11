---
description: Run tests for a2a_demo containers — smoke tests and manual verification
---

# Testing Workflow

> No automated test framework is configured. Tests are manual/smoke tests via curl or the A2A Inspector.

## Smoke Test: Agent Cards
// turbo
```bash
curl -s http://localhost:8001/.well-known/agent-card.json | python -m json.tool
curl -s http://localhost:8002/.well-known/agent-card.json | python -m json.tool
curl -s http://localhost:8003/.well-known/agent-card.json | python -m json.tool
```
All should return valid JSON with `id`, `name`, `skills`.

## Functional Test: Direct Response (agent3)
```bash
curl -X POST http://localhost:8003 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"t1","method":"message/send","params":{"message":{"messageId":"m1","role":"user","parts":[{"kind":"text","text":"What is 2 + 2?"}]}}}'
```
Expected: response contains `"4"` or similar.

## Functional Test: Email Routing
```bash
curl -X POST http://localhost:8003 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"t2","method":"message/send","params":{"message":{"messageId":"m2","role":"user","parts":[{"kind":"text","text":"Send an email to test@example.com saying hello from A2A"}]}}}'
```
Expected: routed to agent1, response contains `"Email sent successfully"`.

## Functional Test: Sheets Routing
```bash
curl -X POST http://localhost:8003 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"t3","method":"message/send","params":{"message":{"messageId":"m3","role":"user","parts":[{"kind":"text","text":"Create a spreadsheet called Test Sheet"}]}}}'
```
Expected: routed to agent2, response contains `"created successfully"`.

## container_test.py
A basic connectivity test exists at project root:
```bash
python container_test.py
```

## A2A Inspector UI Testing
1. Open `http://localhost:4000`
2. Connect to `http://localhost:8003`
3. Use the Inspector UI to send messages interactively
4. Inspect task history, message parts, and status updates

## Adding Unit Tests (Future)

When adding tests, use:
- **pytest** for Python unit tests
- **pytest-asyncio** for async tests
- Mock A2A types from `a2a.types`
- `InMemoryTaskStore` is already usable in tests

Install test dependencies:
```bash
pip install pytest pytest-asyncio
```
