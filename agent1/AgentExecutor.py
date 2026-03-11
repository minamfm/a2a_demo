import os
import base64
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.message import EmailMessage

from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import (
    Message,
    Role, 
    Part,
    TextPart,
    TaskStatus, 
    TaskState,
    TaskStatusUpdateEvent
)

def get_gmail_service():
    scopes = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("token.json is missing or invalid. Please authenticate locally first.")
    return build('gmail', 'v1', credentials=creds)

@tool
def send_email(to_address: str, subject: str, body: str) -> str:
    """Sends an email using Gmail API."""
    try:
        service = get_gmail_service()
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to_address
        message['Subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        return f"Email sent successfully to {to_address}. Message ID: {send_message['id']}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

# Define langgraph agent
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")
langgraph_agent = create_react_agent(llm, tools=[send_email])

class EmailAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_message_text = context.get_user_input()

        if not user_message_text:
            return

        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.working),
                final=False
            )
        )

        result = await langgraph_agent.ainvoke({"messages": [("user", user_message_text)]})
        response_text = result["messages"][-1].content
        if isinstance(response_text, list):
            response_text = "".join([p.get("text", "") if isinstance(p, dict) else str(p) for p in response_text])

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

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.canceled),
                final=True
            )
        )
