from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.server.apps.jsonrpc.fastapi_app import A2AFastAPIApplication

from AgentCard import agent_card
from AgentExecutor import TemplateAgentExecutor

# A2A Boilerplate for building the application
task_store = InMemoryTaskStore()
request_handler = DefaultRequestHandler(
    agent_executor=TemplateAgentExecutor(),
    task_store=task_store
)
app = A2AFastAPIApplication(
    agent_card=agent_card,
    http_handler=request_handler
).build()

if __name__ == "__main__":
    import uvicorn
    # Make sure to set any required environment variables (like GOOGLE_API_KEY) before running
    uvicorn.run(app, host="0.0.0.0", port=8000)
