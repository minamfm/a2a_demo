# A2A LangGraph Agent Template

This template provides a starting point for building [A2A-compliant](https://github.com/google-gemini/a2a-sdk) agents using [LangGraph](https://github.com/langchain-ai/langgraph).

## How to Code Your Own A2A Agent

Follow these steps to customize this template and build your own agent:

### 1. Define Your Agent's Identity (`AgentCard.py`)
Open `AgentCard.py` and update the `agent_card` object:
- **`id`**: A unique string identifier for your agent.
- **`name`**: The display name for your agent.
- **`description`**: A clear description of what your agent does. This is used by other agents (orchestrators) to discover and route tasks to your agent.
- **`skills`**: List the specific capabilities of your agent. Each `AgentSkill` should have a description and examples of how to trigger it.

### 2. Implement Your Agent's Logic (`AgentExecutor.py`)
This file is where the core functionality of your agent resides.

- **Add Tools**: Use the `@tool` decorator from `langchain_core.tools` to define functions your agent can call.
  ```python
  @tool
  def my_custom_tool(param: str) -> str:
      """Description of what this tool does."""
      return f"Result: {param}"
  ```
- **Configure the LLM**: Update the `llm` variable with your preferred model (e.g., `gemini-1.5-flash` or `gemini-1.5-pro`).
- **Define the Graph**: By default, it uses `create_react_agent`. You can replace this with a custom LangGraph `StateGraph` for more complex workflows.
- **Process A2A Requests**: The `TemplateAgentExecutor.execute` method handles incoming A2A tasks. It extracts the user input, invokes the LangGraph agent, and sends back the response using `event_queue.enqueue_event`.

### 3. Manage Dependencies (`requirements.txt`)
If your custom tools require additional Python libraries (e.g., `requests`, `pandas`, `google-api-python-client`), add them to `requirements.txt`.

### 4. Set Environment Variables
Your agent needs an API key to communicate with the LLM.
```bash
export GOOGLE_API_KEY="your-api-key"
```

### 5. Run Your Agent
Install dependencies and start the FastAPI server:
```bash
pip install -r requirements.txt
python main.py
```
The agent will be running at `http://localhost:8000`.

---

## Testing with A2A Inspector

The **A2A Inspector** is a web-based tool that allows you to interact with and debug your A2A agents.

### Download and Run the Inspector
You can run the inspector using Docker:

1. **Pull the image**:
   ```bash
   docker pull a2aprotocol/inspector:latest
   ```

2. **Run the container**:
   ```bash
   docker run -p 3000:3000 a2aprotocol/inspector:latest
   ```

3. **Open the Inspector**:
   Navigate to [http://localhost:3000](http://localhost:3000) in your browser.

### Connect to Your Agent
1. In the Inspector UI, enter your agent's URL: `http://localhost:8000` (or `http://host.docker.internal:8000` if the inspector is running in a container and your agent is running on the host).
2. You can now send messages to your agent and see the JSON-RPC traffic, task status updates, and final responses.

---

## File Structure
- `main.py`: Entry point that builds the A2AFastAPIApplication.
- `AgentExecutor.py`: Bridges LangGraph logic with the A2A protocol.
- `AgentCard.py`: Metadata for agent discovery and identification.
- `requirements.txt`: Project dependencies.
- `Dockerfile`: Used for containerizing your agent.
