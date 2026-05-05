import asyncio
import websockets
import json

async def simulate_twilio():
    uri = "ws://localhost:8000/twilio-stream"
    async with websockets.connect(uri) as websocket:
        # Simulate Twilio starting a call
        start_msg = {
            "event": "start",
            "start": {
                "streamSid": "test-stream-sid-1234"
            }
        }
        await websocket.send(json.dumps(start_msg))
        print("Sent start event")
        
        # Wait a bit to let it process
        await asyncio.sleep(2)
        
        # Send some mock audio? The backend expects audio, but we can just wait to let it connect to Gemini
        # We can close it after a few seconds
        
        stop_msg = {
            "event": "stop"
        }
        await websocket.send(json.dumps(stop_msg))
        print("Sent stop event")

if __name__ == "__main__":
    asyncio.run(simulate_twilio())
