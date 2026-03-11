import uuid
import asyncio
from typing import List, Dict, Any, Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import (
    Message,
    Role, 
    Part,
    TaskStatus, 
    TaskState,
    TaskStatusUpdateEvent
)

# 1. Define Tools
@tool
def sample_tool(query: str) -> str:
    """A sample tool for the agent to use."""
    return f"Tool output for query: {query}"

# 2. Define LangGraph Agent (using prebuilt ReAct agent as default)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash") # Change to your preferred model
tools = [sample_tool]
langgraph_agent = create_react_agent(llm, tools=tools)

# 3. Implement A2A AgentExecutor
class TemplateAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_message_text = context.get_user_input()

        if not user_message_text:
            return

        # Signal that the agent has started working
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.working),
                final=False
            )
        )

        try:
            # Invoke the LangGraph agent
            # Note: LangGraph's ainvoke expects a dict (often with "messages" key)
            result = await langgraph_agent.ainvoke({"messages": [("user", user_message_text)]})
            
            # Extract text from the last message in LangGraph history
            response_text = result["messages"][-1].content
            if isinstance(response_text, list):
                response_text = "".join([p.get("text", "") if isinstance(p, dict) else str(p) for p in response_text])

            # Prepare the A2A response message
            response_message = Message(
                message_id=str(uuid.uuid4()),
                context_id=context.context_id,
                task_id=context.task_id,
                role=Role.agent,
                parts=[Part(text=response_text)]
            )

            # Send the response message
            await event_queue.enqueue_event(response_message)

            # Signal that the task is completed
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(state=TaskState.completed),
                    final=True
                )
            )

        except Exception as e:
            # Handle and report errors via A2A
            error_message = Message(
                message_id=str(uuid.uuid4()),
                context_id=context.context_id,
                task_id=context.task_id,
                role=Role.agent,
                parts=[Part(text=f"Error: {str(e)}")]
            )
            await event_queue.enqueue_event(error_message)
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(state=TaskState.failed),
                    final=True
                )
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Handle task cancellation."""
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.canceled),
                final=True
            )
        )
