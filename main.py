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
from services.firebase_service import init_firebase, sync_call_to_firestore, send_push_notification
import random
import os
import sys

# 1. Startup Environment Validation
REQUIRED_ENV_VARS = ["GEMINI_API_KEY", "PINECONE_API_KEY"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
if missing_vars:
    print(f"CRITICAL ERROR: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set them in your .env file or environment.")
    # In a real app we might sys.exit(1), but for FastAPI we'll just log loudly
    # sys.exit(1)

app = FastAPI(title="VaaniAI RM Intelligence Server")

@app.on_event("startup")
async def startup_event():
    init_db()
    init_firebase()
    print("Database and Firebase initialized.")

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

@app.get("/api/knowledge-base")
async def fetch_knowledge_base():
    # This matches the data seeded in scripts/seed_kb.py
    return [
        {"id": "prod_1", "title": "Tractor Loans", "content": "Loans for Mahindra, John Deere, etc. 8.5% interest, up to 7 years."},
        {"id": "prod_2", "title": "Crop Insurance", "content": "Kharif (2%) and Rabi (1.5%) crop protection. 30-day claim settlement."},
        {"id": "prod_3", "title": "Digital Mandi", "content": "Real-time market prices, direct buyer connections, 1% commission."},
        {"id": "company_info", "title": "About VaaniAI", "content": "AI-first Relationship Manager for rural India supporting EN, HI, TA."}
    ]

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
                        
                        # Create a demo lead entry in DB
                        # For hackathon demo, we use a predictable lead if not provided
                        demo_names = ["Ramesh Singh", "Sunita Devi", "Amit Patel", "Priya Sharma"]
                        demo_phones = ["+91 98765 43210", "+91 91234 56780", "+91 99887 77665", "+91 98765 11223"]
                        idx = random.randint(0, len(demo_names)-1)
                        
                        create_call(stream_sid, demo_names[idx], demo_phones[idx])
                        
                        # Add initial greeting message to DB
                        from services.database import add_message
                        import uuid
                        greeting = f"Namaste {demo_names[idx]} Ji! Main VaaniAI se baat kar rahi hoon. Kya main aapki madad kar sakti hoon?"
                        add_message(stream_sid, str(uuid.uuid4()), 'ai', greeting)
                        
                        print(f"Started Media Stream: {stream_sid} for {demo_names[idx]}")
                        
                    elif event == "media":
                        payload = msg["media"]["payload"]
                        # Forward audio chunk to Gemini
                        gemini_chunk = prepare_gemini_audio_chunk(payload)
                        await gemini_ws.send(gemini_chunk)
                        
                    elif event == "stop":
                        print(f"Stream stopped by Twilio: {stream_sid}")
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
            # Sync final state to Firestore
            call_data = get_call_by_id(stream_sid)
            if call_data:
                sync_call_to_firestore(call_data)
                send_push_notification(
                    "Call Concluded", 
                    f"Relationship Manager session with {call_data['customerName']} ended."
                )
        print("Session ended.")

from services.tts_service import synthesize
from services.gemini_stream import transcribe_audio
from google import genai
import websockets

@app.websocket("/voice-stream")
async def voice_stream(websocket: WebSocket):
    await websocket.accept()
    print("Voice WebSocket connected!")

    try:
        from services.database import add_message
        import uuid
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "DUMMY_KEY"))
        
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            call_id = payload.get("call_id")

            if payload["event"] == "audio":
                audio_bytes = base64.b64decode(payload["payload"])
                lang = payload.get("lang", "en-US")
                
                # STT
                text = await transcribe_audio(audio_bytes, lang)
                
                if text:
                    await websocket.send_text(json.dumps({"event": "transcript", "text": text}))
                    if call_id:
                        add_message(call_id, str(uuid.uuid4()), "customer", text)
                    
                    # LLM
                    system_prompt = f"You are VaaniAI, a professional Relationship Manager for rural India. Answer the following query concisely and clearly in the {lang} language. Keep the response brief, around 1-3 sentences. Ensure you use respectful terms."
                    
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=[system_prompt, text]
                    )
                    ai_text = response.text
                    if call_id:
                        add_message(call_id, str(uuid.uuid4()), "ai", ai_text)
                    
                    # TTS
                    tts_bytes = synthesize(ai_text, language_code=lang)
                    if tts_bytes:
                        audio_b64 = base64.b64encode(tts_bytes).decode("utf-8")
                        await websocket.send_text(json.dumps({"event": "audio", "payload": audio_b64}))

            elif payload["event"] == "text":
                text = payload.get("payload", "")
                lang = payload.get("lang", "en-US")
                
                if text:
                    await websocket.send_text(json.dumps({"event": "transcript", "text": text}))
                    if call_id:
                        add_message(call_id, str(uuid.uuid4()), "customer", text)
                    
                    system_prompt = f"You are VaaniAI, a professional Relationship Manager for rural India. Answer the following query concisely and clearly in the {lang} language. Keep the response brief, around 1-3 sentences. Ensure you use respectful terms."
                    
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=[system_prompt, text]
                    )
                    ai_text = response.text
                    if call_id:
                        add_message(call_id, str(uuid.uuid4()), "ai", ai_text)
                    
                    tts_bytes = synthesize(ai_text, language_code=lang)
                    if tts_bytes:
                        audio_b64 = base64.b64encode(tts_bytes).decode("utf-8")
                        await websocket.send_text(json.dumps({"event": "audio", "payload": audio_b64}))
                        
    except WebSocketDisconnect:
        print("Voice WebSocket disconnected")
    except Exception as e:
        print(f"Error in voice_stream: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
