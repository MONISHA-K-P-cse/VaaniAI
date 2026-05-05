import os
import json
import base64
import websockets
from services.audio_utils import twilio_to_gemini, gemini_to_twilio
from services.rag_service import query_knowledge_base
from services.language_router import detect_language
from services.sentiment_handler import evaluate_intervention, trigger_discount_offer

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "DUMMY_KEY")
GEMINI_WS_URL = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={GEMINI_API_KEY}"

def get_system_instruction(language="English"):
    base_prompt = "You must constantly evaluate the user's emotional tone from their voice. If they sound Frustrated or Skeptical, immediately call the trigger_discount_offer tool."
    
    if language == "Hindi":
        lang_prompt = "Namaste! Aap ek helpful AI assistant hain. Aapko humesha Hinglish mein baat karni hai, aur 'Ji' aur 'Aap' ka istemaal karna hai. Keep responses brief."
    elif language == "Tamil":
        lang_prompt = "You are a helpful AI assistant. Always speak in fluent conversational Tamil. Keep responses brief."
    else:
        lang_prompt = "You are a helpful AI assistant. Speak in English. Keep responses brief and helpful."
        
    return f"{lang_prompt} {base_prompt}"

async def connect_to_gemini():
    import ssl
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    gemini_ws = await websockets.connect(GEMINI_WS_URL, ssl=ssl_context)
    
    setup_msg = {
        "setup": {
            "model": "models/gemini-1.5-flash",
            "systemInstruction": {
                "parts": [{"text": get_system_instruction("English")}]
            },
            "tools": [
                {
                    "functionDeclarations": [{
                        "name": "query_knowledge_base",
                        "description": "Searches the product knowledge base for details about a product. Call this when the user asks a question about a product.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "query": {
                                    "type": "STRING",
                                    "description": "The user's specific query about a product."
                                }
                            },
                            "required": ["query"]
                        }
                    }]
                },
                {
                    "functionDeclarations": [{
                        "name": "trigger_discount_offer",
                        "description": "Call this tool IMMEDIATELY if you detect that the user is frustrated, angry, or skeptical based on their vocal tone or words.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "sentiment": {
                                    "type": "STRING",
                                    "description": "The detected emotion (e.g., 'Frustrated', 'Skeptical')."
                                }
                            },
                            "required": ["sentiment"]
                        }
                    }]
                }
            ],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": "Puck"
                        }
                    }
                }
            }
        }
    }
    await gemini_ws.send(json.dumps(setup_msg))
    setup_response = await gemini_ws.recv()
    print("Gemini Setup Response:", setup_response)
    
    return gemini_ws

def prepare_gemini_audio_chunk(ulaw_payload: str) -> str:
    ulaw_bytes = base64.b64decode(ulaw_payload)
    pcm_bytes = twilio_to_gemini(ulaw_bytes)
    pcm_b64 = base64.b64encode(pcm_bytes).decode('utf-8')
    
    msg = {
        "clientContent": {
            "turns": [{
                "role": "user",
                "parts": [{
                    "inlineData": {
                        "mimeType": "audio/pcm;rate=16000",
                        "data": pcm_b64
                    }
                }]
            }],
            "turnComplete": False
        }
    }
    return json.dumps(msg)

async def handle_gemini_message(gemini_ws, json_str: str, current_lang_state: dict, stream_sid: str = None):
    """
    Parses Gemini's response.
    Returns (ulaw_bytes, None) if audio is present.
    Returns (None, new_lang) if a tool call was handled and language was updated.
    """
    try:
        data = json.loads(json_str)
        
        # 1. Handle Audio Response
        if "serverContent" in data:
            model_turn = data["serverContent"].get("modelTurn", {})
            for part in model_turn.get("parts", []):
                if "text" in part and stream_sid:
                    from services.database import add_message
                    import uuid
                    add_message(stream_sid, str(uuid.uuid4()), "ai", part["text"])
                if "inlineData" in part and "data" in part["inlineData"]:
                    pcm_bytes = base64.b64decode(part["inlineData"]["data"])
                    ulaw_bytes = gemini_to_twilio(pcm_bytes)
                    return ulaw_bytes, None

        # 2. Handle Tool Calls
        elif "toolCall" in data:
            tool_call = data["toolCall"]
            for call in tool_call.get("functionCalls", []):
                
                # RAG Tool
                if call["name"] == "query_knowledge_base":
                    query = call.get("args", {}).get("query", "")
                    print(f"Tool Call Triggered (RAG): {query}")
                    
                    # Language Routing
                    detected_lang = detect_language(query)
                    if detected_lang != current_lang_state["lang"]:
                        print(f"Language Switch Detected: {current_lang_state['lang']} -> {detected_lang}")
                        current_lang_state["lang"] = detected_lang
                        
                        # Send context update to force persona switch
                        context_msg = {
                            "clientContent": {
                                "turns": [{
                                    "role": "user",
                                    "parts": [{"text": f"SYSTEM NOTE: The user is now speaking {detected_lang}. {get_system_instruction(detected_lang)}"}]
                                }],
                                "turnComplete": True
                            }
                        }
                        await gemini_ws.send(json.dumps(context_msg))
                    
                    # Query RAG
                    rag_result = query_knowledge_base(query, current_lang_state["lang"])
                    
                    # Send Tool Response
                    resp_msg = {
                        "toolResponse": {
                            "functionResponses": [{
                                "id": call["id"],
                                "name": call["name"],
                                "response": {"result": rag_result}
                            }]
                        }
                    }
                    await gemini_ws.send(json.dumps(resp_msg))
                    return None, current_lang_state["lang"]
                
                # Sentiment/Discount Tool
                elif call["name"] == "trigger_discount_offer":
                    sentiment = call.get("args", {}).get("sentiment", "")
                    print(f"Tool Call Triggered (Sentiment): detected {sentiment}")
                    
                    if stream_sid:
                        from services.database import update_call_score
                        update_call_score(stream_sid, 3) # Lower score to indicate bad sentiment
                        
                    if evaluate_intervention(sentiment):
                        discount_msg = trigger_discount_offer()
                        
                        # Inject a tone adjustment message
                        tone_override_msg = {
                            "clientContent": {
                                "turns": [{
                                    "role": "user",
                                    "parts": [{"text": "SYSTEM OVERRIDE: The user is frustrated. Immediately adopt an extremely Apologetic and Reassuring tone."}]
                                }],
                                "turnComplete": True
                            }
                        }
                        await gemini_ws.send(json.dumps(tone_override_msg))
                        
                        # Return discount code
                        resp_msg = {
                            "toolResponse": {
                                "functionResponses": [{
                                    "id": call["id"],
                                    "name": call["name"],
                                    "response": {"result": discount_msg}
                                }]
                            }
                        }
                        await gemini_ws.send(json.dumps(resp_msg))
                    else:
                        # Return no discount needed
                        resp_msg = {
                            "toolResponse": {
                                "functionResponses": [{
                                    "id": call["id"],
                                    "name": call["name"],
                                    "response": {"result": "No intervention required."}
                                }]
                            }
                        }
                        await gemini_ws.send(json.dumps(resp_msg))
                        
                    return None, current_lang_state["lang"]
                    
    except Exception as e:
        print("Error handling Gemini message:", e)
        
    return None, None
