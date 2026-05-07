import os
import json
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "DUMMY_KEY"))

class PostCallOutput(BaseModel):
    summary: str
    next_steps: list[str]
    whatsapp_message: str

def generate_post_call_data(transcript: str, customer_name: str) -> dict:
    """
    Uses Gemini 3.1 Pro to summarize the call, extract next steps, and generate a WhatsApp message.
    """
    try:
        system_prompt = f"""
        You are a post-call analyst for VaaniAI. Analyze the provided transcript.
        Extract a brief summary (2-3 sentences), and a list of actionable Next Steps.
        Also, write a personalized WhatsApp follow-up message to the customer ({customer_name}).
        The message should be in Hinglish, polite (using Ji/Aap), and MUST include the sign-up link: https://vaaniai.com/signup
        
        Respond in JSON matching this schema:
        {{
            "summary": "...",
            "next_steps": ["...", "..."],
            "whatsapp_message": "..."
        }}
        """
        
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=f"Transcript:\n{transcript}",
            config={
                "system_instruction": system_prompt,
                "response_mime_type": "application/json",
                "response_schema": PostCallOutput
            }
        )
        
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"Error in post call generation: {e}")
        return {
            "summary": "Detailed summary generation was skipped or encountered an error.",
            "next_steps": ["Follow up on tractor loan details.", "Verify documents."],
            "whatsapp_message": f"Namaste {customer_name} Ji, humari call ke liye shukriya. Aap is link par sign up kar sakte hain: https://vaaniai.com/signup"
        }

def send_whatsapp_followup(message: str, phone: str) -> bool:
    """
    Mocks a WATI API call to send the generated message.
    """
    print(f"\n[WATI MOCK] Sending WhatsApp to {phone}:\n{message}\n")
    return True
