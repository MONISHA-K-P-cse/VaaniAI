import edge_tts
import io

VOICE_MAP = {
    "en": "en-IN-NeerjaNeural",
    "hi": "hi-IN-MadhurNeural",
    "kn": "kn-IN-GaganNeural"
}

async def synthesize(text: str, language_code: str = "en-US") -> bytes:
    """
    Convert plain text to audio using the edge-tts library (Neural Voices).
    No API key required! Higher quality than gTTS.
    """
    lang = language_code.split('-')[0]
    voice = VOICE_MAP.get(lang, "en-IN-NeerjaNeural")
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        # Collect chunks into bytes
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data
    except Exception as e:
        print(f"Error in edge-tts synthesis: {e}")
        return b""
