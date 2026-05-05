import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Initialize the Gemini client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY is not set in the .env file.")
    exit(1)

client = genai.Client(api_key=api_key)

prompt = "You are Vaani, an empathetic relationship manager. Greet a customer in a mix of Hindi and English who is asking about a home loan."

print(f"Sending prompt to Gemini 2.5 Flash:\n'{prompt}'\n")

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    print("Response from Vaani:")
    print("-" * 40)
    print(response.text)
    print("-" * 40)
except Exception as e:
    print(f"Error communicating with Gemini API: {e}")
