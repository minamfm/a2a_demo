# A2A Demo

This project demonstrates an Agent-to-Agent (A2A) protocol system with 3 agents:
1. **Agent 1 (Email)**: Built with LangGraph. Can send emails via Gmail.
2. **Agent 2 (Sheets)**: Built with Google GenAI SDK. Can create Google Sheets.
3. **Agent 3 (Orchestrator)**: Built with LangGraph. Discovers Agent 1 and Agent 2, and dynamically routes queries to the appropriate agent based on their `agent-card.json`.

An **A2A Inspector** is also included to easily test and inspect Agent 3 from the browser.

## Prerequisites

1. Prepare your `.env` file with `GEMINI_API_KEY`:
   ```bash
   cp .env.example .env
   # Edit .env and supply your key!
   ```

2. Google Workspace Authentication (`credentials.json` & `token.json`):
   - Agent 1 and Agent 2 require access to your Google Account (Gmail & Sheets).
   - Place your `credentials.json` (OAuth Client ID desktop credentials) and `token.json` (authenticated session) at the root of `z:/A2A Demo/`.
   - If you don't have a `token.json` yet, you can run a quick local script `python generate_token.py` (which I can help you create) to log in through your browser and save the `token.json`.

## Running the Demo

1. Build and bring up the docker containers:
   ```bash
   docker-compose up -d --build
   ```

2. Wait a few seconds for all agents to start and discover each other.

3. Open the **A2A Inspector** in your browser: [http://localhost:3000](http://localhost:3000)

4. In the Inspector, specify the orchestrator URL to connect to it:
   - Endpoint: `http://agent3:8000`
   - Since you run it inside Docker network, you might need to try `http://localhost:8003` from your local browser if the inspector runs purely client-side! If the inspector docker image acts as a proxy, use `http://agent3:8000`. Give it a try!

## Validating Agent Routing
From the Inspector or via API:
1. Ask: *"Send an email to [your-email] saying Hello from A2A!"* 
   -> Agent 3 routes to Agent 1 -> Email is sent.
2. Ask: *"Create a spreadsheet tracking my groceries."* 
   -> Agent 3 routes to Agent 2 -> Sheet is created.
