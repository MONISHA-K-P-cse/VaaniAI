import asyncio
import websockets
import json
import base64
import time

WS_URL = "ws://localhost:8000/twilio-stream"

async def mock_twilio_client():
    try:
        async with websockets.connect(WS_URL) as ws:
            print("Connected to VaaniAI server.")
            
            # 1. Send Connected Event
            await ws.send(json.dumps({
                "event": "connected",
                "protocol": "Call",
                "version": "1.0.0"
            }))
            
            # 2. Send Start Event
            await ws.send(json.dumps({
                "event": "start",
                "sequenceNumber": "1",
                "start": {
                    "streamSid": "MZmock1234567890",
                    "accountSid": "ACmock1234567890",
                    "callSid": "CAmock1234567890",
                    "tracks": ["inbound"],
                    "mediaFormat": {
                        "encoding": "audio/x-mulaw",
                        "sampleRate": 8000,
                        "channels": 1
                    }
                }
            }))
            
            # 3. Stream dummy audio payload
            # For testing, we just send a zero-filled byte array representing silence
            # (or very quiet static). 160 bytes of u-law = 20ms of audio
            dummy_ulaw = b'\xff' * 160
            dummy_b64 = base64.b64encode(dummy_ulaw).decode('utf-8')
            
            print("Streaming mock audio packets...")
            start_time = time.time()
            
            for i in range(10):
                await ws.send(json.dumps({
                    "event": "media",
                    "sequenceNumber": str(i + 2),
                    "media": {
                        "track": "inbound",
                        "chunk": str(i),
                        "timestamp": str(i * 20),
                        "payload": dummy_b64
                    },
                    "streamSid": "MZmock1234567890"
                }))
                await asyncio.sleep(0.02) # 20ms pacing
                
            # Listen for response (timing the latency)
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                end_time = time.time()
                latency = (end_time - start_time) * 1000
                print(f"Received response from server in {latency:.2f} ms")
                print("Response packet:", response[:100], "...")
            except asyncio.TimeoutError:
                print("No immediate response (Expected since we sent silence, or Gemini API key is missing).")
            
            # 4. Stop Event
            await ws.send(json.dumps({
                "event": "stop",
                "sequenceNumber": "12",
                "streamSid": "MZmock1234567890",
                "stop": {
                    "accountSid": "ACmock1234567890",
                    "callSid": "CAmock1234567890"
                }
            }))
            print("Mock session complete.")
            
    except ConnectionRefusedError:
        print("Could not connect to server. Ensure main.py is running on port 8000.")

if __name__ == "__main__":
    asyncio.run(mock_twilio_client())
