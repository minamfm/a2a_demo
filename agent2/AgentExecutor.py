import os
import uuid
from google import genai
from google.genai import types
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

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

def get_sheets_service():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("token.json is missing or invalid. Please authenticate locally first.")
    return build('sheets', 'v4', credentials=creds)

def create_spreadsheet(title: str) -> str:
    """Creates a new Google Spreadsheet with the given title."""
    try:
        service = get_sheets_service()
        spreadsheet = {'properties': {'title': title}}
        spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
        return f"Spreadsheet '{title}' created successfully! ID: {spreadsheet.get('spreadsheetId')}"
    except Exception as e:
        return f"Failed to create spreadsheet: {str(e)}"

def append_spreadsheet_values(spreadsheet_id: str, range_name: str, values: list[list[str]]) -> str:
    """Appends values to a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_name: The A1 notation of the range to append to.
        values: A list of lists representing rows of strings to append.
    """
    try:
        service = get_sheets_service()
        body = {'values': values}
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption="USER_ENTERED", body=body).execute()
        return f"{result.get('updates').get('updatedCells')} cells appended."
    except Exception as e:
        return f"Failed to append values: {str(e)}"

# Setup GenAI client
client = genai.Client()

class SheetsAgentExecutor(AgentExecutor):
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

        config = types.GenerateContentConfig(
            tools=[create_spreadsheet, append_spreadsheet_values],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )
        chat_session = client.chats.create(model="gemini-3.1-flash-lite-preview", config=config)
        
        response = chat_session.send_message(user_message_text)
        
        # Handle function execution
        print(f"[DEBUG] SheetsAgentExecutor starting tool loop for task: {context.task_id}")
        for i in range(10): # Loop limit for complex tasks
            if response.function_calls:
                print(f"[DEBUG] Iteration {i}: Received {len(response.function_calls)} function calls")
                responses = []
                for func_call in response.function_calls:
                    print(f"[DEBUG] Executing tool: {func_call.name}")
                    if func_call.name == "create_spreadsheet":
                        args = func_call.args
                        title = args.get("title", "Untitled")
                        result = create_spreadsheet(title=title)
                        responses.append(
                            types.Part.from_function_response(
                                name=func_call.name,
                                response={"result": result}
                            )
                        )
                    elif func_call.name == "append_spreadsheet_values":
                        args = func_call.args
                        result = append_spreadsheet_values(
                            spreadsheet_id=args.get("spreadsheet_id"),
                            range_name=args.get("range_name", "Sheet1!A1"),
                            values=args.get("values", [])
                        )
                        responses.append(
                            types.Part.from_function_response(
                                name=func_call.name,
                                response={"result": result}
                            )
                        )
                response = chat_session.send_message(responses)
            else:
                break
                
        response_message = Message(
            message_id=str(uuid.uuid4()),
            context_id=context.context_id,
            task_id=context.task_id,
            role=Role.agent,
            parts=[Part(text=response.text)]
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
