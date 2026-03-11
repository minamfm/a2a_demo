# Database Reference — a2a_demo

## No Persistent Database

This project uses no SQL, NoSQL, or cache databases. All task state is ephemeral (in-memory).

## InMemoryTaskStore (a2a-sdk)

Each agent instantiates its own `InMemoryTaskStore`. This stores in-flight task objects keyed by task ID.

- **Scope**: Per-container process
- **Persistence**: None — wiped on container restart
- **Access pattern**: Read/write by `DefaultRequestHandler` during task lifecycle

## External Data Stores

### Google Gmail (agent1)

- **Access**: Write-only (agent1 can only send, not read mail)
- **Auth**: `token.json` OAuth2 refresh token (scope: `gmail.send`)
- **Pattern**: One API call per task — no batching, no retry logic

### Google Sheets (agent2)

- **Access**: Create new sheets + append to existing sheets
- **Auth**: `token.json` OAuth2 refresh token (scope: `spreadsheets`)
- **Pattern**: multi-step: `create_spreadsheet()` first, then optionally `append_spreadsheet_values()`

## Adding Persistent Storage

If you need persistent task storage in a future iteration:
1. Replace `InMemoryTaskStore` with a custom implementation of the `TaskStore` interface from `a2a.server.tasks`
2. Use Redis or PostgreSQL as a backing store
3. Update `requirements.txt` with the relevant client library
