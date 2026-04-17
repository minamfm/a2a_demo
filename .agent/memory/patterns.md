# Patterns — a2a_demo

## Agent Bootstrap Pattern (same for all three agents)

```python
# main.py — identical structure in agent1, agent2, agent3
from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.server.apps.jsonrpc.fastapi_app import A2AFastAPIApplication
from AgentCard import agent_card
from AgentExecutor import MyAgentExecutor

task_store = InMemoryTaskStore()
request_handler = DefaultRequestHandler(
    agent_executor=MyAgentExecutor(),
    task_store=task_store
)
app = A2AFastAPIApplication(
    agent_card=agent_card,
    http_handler=request_handler
).build()
```

## AgentExecutor Pattern

All executors implement the `AgentExecutor` interface:

```python
class MyAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = context.get_user_input()
        if not user_text:
            return
        # 1. Signal working
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(..., status=TaskStatus(state=TaskState.working), final=False)
        )
        # 2. Do work (call LLM / API)
        result = ...
        # 3. Enqueue response message
        await event_queue.enqueue_event(
            Message(role=Role.agent, parts=[Part(text=result)])
        )
        # 4. Signal completed
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(..., status=TaskStatus(state=TaskState.completed), final=True)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(..., status=TaskStatus(state=TaskState.canceled), final=True)
        )
```

## AgentCard Declaration Pattern

```python
from a2a.types import AgentCard, AgentSkill

agent_card = AgentCard(
    id="unique-agent-id",
    name="Human Readable Name",
    description="What this agent does.",
    version="1.0.0",
    url="http://service-name:8000",           # Docker DNS service name
    capabilities={"streaming": False},
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(
            id="skill_id",
            name="Skill Name",
            description="What this skill does — used by orchestrator for routing.",
            tags=["tag1", "tag2"],
            examples=["Example prompt"]
        )
    ]
)
```

## LangGraph ReAct Pattern (agent1, langgraph_template)

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """Tool description for LLM."""
    return "result"

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")
langgraph_agent = create_react_agent(llm, tools=[my_tool])

# In execute():
result = await langgraph_agent.ainvoke({"messages": [("user", user_text)]})
response_text = result["messages"][-1].content
if isinstance(response_text, list):
    response_text = "".join([p.get("text", "") if isinstance(p, dict) else str(p) for p in response_text])
```

## GenAI SDK Function Calling Pattern (agent2)

```python
from google import genai
from google.genai import types

client = genai.Client()

def my_function(param: str) -> str:
    """Used directly as tool — no @tool decorator needed."""
    return "result"

config = types.GenerateContentConfig(
    tools=[my_function],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
)
chat = client.chats.create(model="gemini-3.1-flash-lite-preview", config=config)
response = chat.send_message(user_text)

# Manual tool loop
for _ in range(10):
    if response.function_calls:
        responses = []
        for fc in response.function_calls:
            result = my_function(**fc.args)
            responses.append(types.Part.from_function_response(name=fc.name, response={"result": result}))
        response = chat.send_message(responses)
    else:
        break
```

## A2A Client Pattern (agent3 calling other agents)

```python
from a2a.client.client_factory import ClientFactory
from a2a.client.client import ClientConfig
import httpx

async with httpx.AsyncClient(timeout=300.0) as http_client:
    client_config = ClientConfig(httpx_client=http_client)
    client = await ClientFactory.connect(agent_url, client_config=client_config)
    
    request_msg = Message(
        message_id=str(uuid.uuid4()),
        role=Role.user,
        parts=[Part(root={"kind": "text", "text": user_input})]
    )
    
    async for event in client.send_message(request_msg):
        if isinstance(event, Message):
            response_text = event.parts[0].text
    
    await client.close()
```

## Error Handling Pattern (agent3 style)

Wrap the entire execute body in try/except and return error as Message:

```python
try:
    # ... main logic ...
except Exception as e:
    import traceback
    err_msg = traceback.format_exc()
    await event_queue.enqueue_event(
        Message(..., parts=[Part(text=f"ERROR: {str(e)}\n\n{err_msg}")])
    )
    await event_queue.enqueue_event(
        TaskStatusUpdateEvent(..., status=TaskStatus(state=TaskState.completed), final=True)
    )
```

## Google OAuth2 Pattern

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def get_service(api, version, scopes):
    creds = Credentials.from_authorized_user_file('token.json', scopes)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build(api, version, credentials=creds)
```
