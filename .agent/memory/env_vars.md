# Environment Variables — a2a_demo

## Variables

| Variable | Purpose | Default | Required | Used By |
|---|---|---|---|---|
| `GEMINI_API_KEY` | Authenticates to Google Gemini API (LLM inference) | None | Yes | agent1, agent2, agent3 |

## How to Configure

```bash
# Create .env file at project root
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

The `docker-compose.yml` references `${GEMINI_API_KEY}` and injects it as a container environment variable.

## Secrets (File-based)

| File | Purpose | Location |
|---|---|---|
| `token.json` | Google OAuth2 refresh token (Gmail + Sheets) | Project root |
| `credentials.json` | OAuth2 Client ID (for generating token.json) | Project root |

These are bind-mounted into containers:
- `agent1`: `./token.json → /app/token.json`
- `agent2`: `./token.json → /app/token.json`

## Notes

- No `.env.example` file exists yet. Create one to document required variables.
- `credentials.json` is not mounted into containers — it is only needed on the host to run `generate_token.py`.
- agent3 does NOT need `token.json` (it only calls Gemini, not Google APIs).
