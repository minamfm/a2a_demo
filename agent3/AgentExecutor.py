import os
import uuid
import asyncio
import httpx
from typing import TypedDict, Literal, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue

from a2a.client.client_factory import ClientFactory
from a2a.client.client import ClientConfig
from a2a.types import (
    AgentCard,
    Message, 
    Role, 
    Part,
    TaskStatus, 
    TaskState,
    TaskStatusUpdateEvent,
    Task
)

# Routing State
class AgentState(TypedDict):
    input: str
    target_agent: str
    response: str
    discovered_agents: dict

class RouteDecision(BaseModel):
    agent_url: str = Field(
        ..., description="The URL of the target agent to route to, or 'direct_response' if none fit."
    )
    reasoning: str = Field(..., description="Why this route was chosen.")

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")

async def discover_agent_cards(start_port: int, end_port: int) -> dict[str, AgentCard]:
    cards = {}
    async with httpx.AsyncClient() as client:
        # In Docker Compose, agents are reachable by their service names
        for service_name in ["agent1", "agent2", "agent3"]:
            url = f"http://{service_name}:8000"
            try:
                print(f"[DEBUG] Attempting to fetch agent card from {url}")
                resp = await client.get(f"{url}/.well-known/agent-card.json", timeout=1.0)
                if resp.status_code == 200:
                    card_data = resp.json()
                    cards[url] = AgentCard.model_validate(card_data)
                    print(f"[DEBUG] Successfully discovered {card_data.get('name')} at {url}")
            except Exception as e:
                print(f"[DEBUG] Failed to reach {url}: {str(e)}")
    return cards

async def router_node(state: AgentState):
    discovered = state.get("discovered_agents", {})
    print(f"[DEBUG] router_node input: '{state['input']}'")
    if not discovered:
        print("[DEBUG] No agents discovered, opting for direct_response.")
        # Prevent self-loop if no agents are found
        return {"target_agent": "direct_response"}

    agent_urls = list(discovered.keys())
    print(f"[DEBUG] Discovered agents: {agent_urls}")
        
    agents_desc = ""
    for url, card in discovered.items():
        skills = "\n".join([f"  - {s.name}: {s.description}" for s in (card.skills or [])]) if card.skills else "  - No specific skills listed"
        agents_desc += f"URL: {url}\nName: {card.name}\nDescription: {card.description}\nSkills:\n{skills}\n\n"

    prompt = f"""
    You are an orchestrator agent. Your job is to route user requests to the most suitable agent based on their agent cards.
    If none of the agents are suitable, you can respond directly yourself by choosing 'direct_response'.
    
    Here are the available agents (DO NOT route to Orchestrator Agent or yourself to avoid loops):
    {agents_desc}
    
    User Input: {state['input']}
    """
    structured_llm = llm.with_structured_output(RouteDecision)
    decision = await structured_llm.ainvoke(prompt)
    
    selected = decision.agent_url
    print(f"[DEBUG] Router selected target: {selected} (Reasoning: {decision.reasoning})")
    # Guard against loops where the Orchestrator picks its own URL
    if selected in discovered and "Orchestrator" in discovered[selected].name:
        print("[DEBUG] Guard: Router selected Orchestrator, defaulting to direct_response.")
        selected = "direct_response"
        
    return {"target_agent": selected}

async def call_downstream_agent(agent_url: str, user_input: str) -> str:
    print(f"[DEBUG] Calling downstream agent at {agent_url} with input: {user_input}")
    try:
        # A2A SDK ClientFactory handles fetching the AgentCard and interacting
        async with httpx.AsyncClient(timeout=300.0) as http_client:
            client_config = ClientConfig(httpx_client=http_client)
            client = await ClientFactory.connect(agent_url, client_config=client_config)
            
            request_msg = Message(
                message_id=str(uuid.uuid4()),
                role=Role.user,
                parts=[Part(root={"kind": "text", "text": user_input})]
            )
            
            final_response = "No response from downstream agent."
            
            try:
                async for event in client.send_message(request_msg):
                    # A2A SDK's send_message yields tuples for streaming or final messages
                    if isinstance(event, Message):
                        if event.parts and len(event.parts) > 0:
                            part = event.parts[0]
                            final_response = getattr(part, "text", None) or (getattr(part, "root", None) and getattr(part.root, "text", None))
                    elif isinstance(event, tuple) and len(event) == 2:
                        task, update = event
                        if isinstance(task, Task) and task.history:
                            # Look at history or update to get the latest message
                            tgt_msg = None
                            if update and getattr(update, "update", None) and isinstance(update.update, Message):
                                tgt_msg = update.update
                            elif task.history[-1].role == Role.agent:
                                tgt_msg = task.history[-1]
                            
                            if tgt_msg and tgt_msg.parts and len(tgt_msg.parts) > 0:
                                part = tgt_msg.parts[0]
                                final_response = getattr(part, "text", None) or (getattr(part, "root", None) and getattr(part.root, "text", None))
                        print(f"[DEBUG] Received event from {agent_url}: {type(event)}")
            except Exception as client_err:
                print(f"[DEBUG] Client error during communication with {agent_url}: {str(client_err)}")
                raise client_err

            await client.close()
            return final_response
    except Exception as e:
        return f"Error communicating with downstream agent: {str(e)}"

async def execute_route_node(state: AgentState):
    target = state["target_agent"]
    user_input = state["input"]
    print(f"[DEBUG] execute_route_node starting for target: {target}")
    
    if target == "direct_response":
        response = await llm.ainvoke(f"User said: {user_input}. Respond contextually.")
        print("[DEBUG] Direct response generated.")
        content = response.content
        if isinstance(content, list):
            content = "".join([p.get("text", "") if isinstance(p, dict) else str(p) for p in content])
        return {"response": content}
    else:
        response = await call_downstream_agent(target, user_input)
        print(f"[DEBUG] Downstream response received: {response[:100]}...")
        return {"response": response}

workflow = StateGraph(AgentState)
workflow.add_node("router", router_node)
workflow.add_node("executor", execute_route_node)

workflow.set_entry_point("router")
workflow.add_edge("router", "executor")
workflow.add_edge("executor", END)
auth_app = workflow.compile()


class OrchestratorAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        print(f"[DEBUG] Agent 3 execute() started for task_id: {context.task_id}")
        user_message_text = context.get_user_input()
        print(f"[DEBUG] Extracted user_message_text: '{user_message_text}'")

        if not user_message_text:
            print("[DEBUG] user_message_text is empty, returning...")
            return

        print(f"[DEBUG] Sending TaskStatusUpdateEvent(working)...")
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.working),
                final=False
            )
        )
        
        try:
            # Discover agents dynamically (Ports 8000 to 8010)
            # Note: We filter out the Orchestrator itself to prevent infinite routing loops
            all_cards = await discover_agent_cards(8000, 8010)
            discovered_agents = {
                url: card for url, card in all_cards.items() 
                if "Orchestrator" not in card.name
            }

            # Run LangGraph orchestrator
            final_state = await auth_app.ainvoke({
                "input": user_message_text,
                "discovered_agents": discovered_agents
            })
            response_text = final_state.get("response", "Could not generate response.")

            response_message = Message(
                message_id=str(uuid.uuid4()),
                context_id=context.context_id,
                task_id=context.task_id,
                role=Role.agent,
                parts=[Part(text=response_text)]
            )

            await event_queue.enqueue_event(response_message)
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(state=TaskState.completed),
                    final=True
                )
            )
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            response_message = Message(
                message_id=str(uuid.uuid4()),
                context_id=context.context_id,
                task_id=context.task_id,
                role=Role.agent,
                parts=[Part(text=f"ERROR: {str(e)}\n\n{err_msg}")]
            )
            await event_queue.enqueue_event(response_message)
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(state=TaskState.completed),
                    final=True
                )
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.canceled),
                final=True
            )
        )
