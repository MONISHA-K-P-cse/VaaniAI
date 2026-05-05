import json
import base64
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from services.gemini_stream import connect_to_gemini, prepare_gemini_audio_chunk, handle_gemini_message
from services.post_call_service import generate_post_call_data, send_whatsapp_followup
from services.database import init_db, get_calls, get_messages, get_call_by_id, create_call, update_call_status
import random

app = FastAPI(title="VaaniAI Twilio WebSocket Server")

@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PostCallRequest(BaseModel):
    call_id: str

@app.get("/api/calls")
async def fetch_calls():
    return get_calls()

@app.get("/api/calls/{call_id}/messages")
async def fetch_messages(call_id: str):
    return get_messages(call_id)

@app.post("/api/post-call")
async def handle_post_call(request: PostCallRequest):
    call_info = get_call_by_id(request.call_id)
    if not call_info:
        return {"error": "Call not found"}
        
    messages = get_messages(request.call_id)
    transcript = "\n".join([f"{'Agent' if m['sender']=='ai' else 'Customer'}: {m['text']}" for m in messages])
    
    print(f"Post-call triggered for {call_info['customerName']}")
    data = generate_post_call_data(transcript, call_info['customerName'])
    success = send_whatsapp_followup(data["whatsapp_message"], call_info['phone'])
    data["whatsapp_sent"] = success
    return data

@app.websocket("/twilio-stream")
async def twilio_stream(websocket: WebSocket):
    await websocket.accept()
    print("Twilio WebSocket connected!")
    
    gemini_ws = None
    stream_sid = None
    # State object to track language across the session
    current_lang_state = {"lang": "English"}
    
    try:
        # Establish connection to Gemini
        gemini_ws = await connect_to_gemini()
        
        async def receive_from_twilio():
            nonlocal stream_sid
            try:
                while True:
                    data = await websocket.receive_text()
                    msg = json.loads(data)
                    event = msg.get("event")
                    
                    if event == "start":
                        stream_sid = msg["start"]["streamSid"]
                        # Create a dummy lead entry in DB for this stream
                        names = ["Ramesh Singh", "Sunita Devi", "Amit Patel", "Priya Sharma"]
                        phones = ["+91 98765 43210", "+91 91234 56780", "+91 99887 77665", "+91 98765 11223"]
                        idx = random.randint(0, len(names)-1)
                        create_call(stream_sid, names[idx], phones[idx])
                        from services.database import add_message
                        import uuid
                        add_message(stream_sid, str(uuid.uuid4()), 'ai', f'Namaste {names[idx]} Ji! Main VaaniAI se baat kar rahi hoon. Kya main aapki madad kar sakti hoon?')
                        add_message(stream_sid, str(uuid.uuid4()), 'customer', 'Haan ji, mujhe janna tha.')
                        print(f"Started Media Stream: {stream_sid}")
                        
                    elif event == "media":
                        payload = msg["media"]["payload"]
                        # Forward audio chunk to Gemini
                        gemini_chunk = prepare_gemini_audio_chunk(payload)
                        await gemini_ws.send(gemini_chunk)
                        
                    elif event == "stop":
                        print("Stream stopped by Twilio")
                        break
                        
            except WebSocketDisconnect:
                print("Twilio WebSocket disconnected")
            except Exception as e:
                print("Error in receive_from_twilio:", e)

        async def receive_from_gemini():
            try:
                while True:
                    gemini_response = await gemini_ws.recv()
                    ulaw_bytes, _ = await handle_gemini_message(gemini_ws, gemini_response, current_lang_state, stream_sid)
                    
                    if ulaw_bytes and stream_sid:
                        # Send audio back to Twilio
                        out_payload = base64.b64encode(ulaw_bytes).decode('utf-8')
                        twilio_msg = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {
                                "payload": out_payload
                            }
                        }
                        await websocket.send_text(json.dumps(twilio_msg))
                        
            except websockets.exceptions.ConnectionClosed:
                print("Gemini WebSocket closed")
            except Exception as e:
                print("Error in receive_from_gemini:", e)

        # Run both loops concurrently
        await asyncio.gather(
            receive_from_twilio(),
            receive_from_gemini()
        )
        
    except Exception as e:
        print("Error setting up stream:", e)
    finally:
        if gemini_ws and not gemini_ws.closed:
            await gemini_ws.close()
        if stream_sid:
            update_call_status(stream_sid, False)
        print("Session ended.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
