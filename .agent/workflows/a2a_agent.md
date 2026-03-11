---
description: Add a new A2A-compliant agent to the a2a_demo system using the LangGraph template
---

# Add New A2A Agent

This workflow guides you through scaffolding, implementing, and integrating a new A2A-compliant agent using the LangGraph template.

## Step 1: Scaffold from Template

Copy the existing template:
```bash
cp -r langgraph_agent_template/ agent4/
```
Replace `agent4` with your descriptive agent name (e.g., `agent_calendar`, `agent_drive`).

## Step 2: Define the Agent Card

Edit `agent4/AgentCard.py`:

```python
from a2a.types import AgentCard, AgentSkill

agent_card = AgentCard(
    id="agent4-unique-id",               # Must be globally unique
    name="Your Agent Name",              # Used for routing decisions — be descriptive
    description="What this agent does.", # One sentence summary
    version="1.0.0",
    url="http://agent4:8000",            # Must match docker-compose service name
    capabilities={"streaming": False},
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(
            id="skill_id",
            name="Skill Name",
            description="Detailed skill description for the orchestrator's routing LLM.",
            tags=["relevant", "tags"],
            examples=["Example prompt that triggers this skill"]
        )
    ]
)
```

## Step 3: Implement the AgentExecutor

Edit `agent4/AgentExecutor.py` — follow the pattern:

```python
from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import Message, Role, Part, TaskStatus, TaskState, TaskStatusUpdateEvent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
import uuid

@tool
def my_tool(param: str) -> str:
    """Tool description used by LLM to decide when to call it."""
    # Your actual implementation here
    return "result"

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")
langgraph_agent = create_react_agent(llm, tools=[my_tool])

class MyAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = context.get_user_input()
        if not user_text:
            return
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(task_id=context.task_id, context_id=context.context_id,
                                  status=TaskStatus(state=TaskState.working), final=False)
        )
        try:
            result = await langgraph_agent.ainvoke({"messages": [("user", user_text)]})
            response_text = result["messages"][-1].content
            if isinstance(response_text, list):
                response_text = "".join([p.get("text", "") if isinstance(p, dict) else str(p) for p in response_text])
            await event_queue.enqueue_event(
                Message(message_id=str(uuid.uuid4()), context_id=context.context_id,
                        task_id=context.task_id, role=Role.agent, parts=[Part(text=response_text)])
            )
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(task_id=context.task_id, context_id=context.context_id,
                                      status=TaskStatus(state=TaskState.completed), final=True)
            )
        except Exception as e:
            import traceback
            await event_queue.enqueue_event(
                Message(message_id=str(uuid.uuid4()), context_id=context.context_id,
                        task_id=context.task_id, role=Role.agent, parts=[Part(text=f"ERROR: {str(e)}\n{traceback.format_exc()}")])
            )
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(task_id=context.task_id, context_id=context.context_id,
                                      status=TaskStatus(state=TaskState.completed), final=True)
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(task_id=context.task_id, context_id=context.context_id,
                                  status=TaskStatus(state=TaskState.canceled), final=True)
        )
```

## Step 4: Update main.py

Edit `agent4/main.py` to import your new executor:
```python
from AgentExecutor import MyAgentExecutor
# Replace TemplateAgentExecutor with MyAgentExecutor
```

## Step 5: Add to docker-compose.yml

```yaml
agent4:
  build: ./agent4
  ports:
    - "8004:8000"
  environment:
    - GEMINI_API_KEY=${GEMINI_API_KEY}
  networks:
    - a2a-network
```

Add any required volume mounts (e.g., `token.json` if using Google APIs).

## Step 6: Deploy and Verify

```bash
docker-compose up -d --build agent4
curl -s http://localhost:8004/.well-known/agent-card.json | python -m json.tool
```

## Step 7: Verify Discovery by agent3

// turbo
```bash
docker-compose logs agent3 | grep "Successfully discovered"
```
agent3 discovers agents dynamically — it will probe `http://agent4:8000` automatically IF you add `"agent4"` to the probe list in `agent3/AgentExecutor.py`:

```python
# In discover_agent_cards():
for service_name in ["agent1", "agent2", "agent3", "agent4"]:   # Add "agent4"
```
Then rebuild agent3.

## A2A Compliance Checklist for New Agents

- [ ] `AgentCard.id` is unique across all agents
- [ ] `AgentCard.url` matches Docker service name
- [ ] `AgentCard.skills[*].description` clearly describes what the skill does (LLM reads this)
- [ ] Agent responds with `TaskState.working` before heavy processing
- [ ] Agent always sends `final=True` in the last event
- [ ] Agent handles cancellation in `cancel()` method
- [ ] Agent Card served at `/.well-known/agent-card.json`
- [ ] Added to `docker-compose.yml` with `networks: [a2a-network]`
- [ ] Added to `discover_agent_cards()` service name list in agent3
