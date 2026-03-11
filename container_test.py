import asyncio
import httpx

async def submit_request():
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "msg-123",
                "role": "USER",
                "parts": [{"text": "Hello, send an email to user@example.com"}]
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post("http://localhost:8000/", json=payload, timeout=20.0)
        print("Status", resp.status_code)
        print("Response Text")
        print(resp.text)

asyncio.run(submit_request())
