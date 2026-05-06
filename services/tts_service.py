import io
from gtts import gTTS

def synthesize(text: str, language_code: str = "en-US") -> bytes:
    """
    Convert plain text to audio using the free gTTS library.
    No API key required!
    `language_code` is typically 'en', 'hi', 'kn', etc.
    """
    # gTTS uses 2-letter language codes (e.g., 'en', 'hi', 'kn')
    lang = language_code.split('-')[0]
    
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue() # Returns raw MP3 bytes
    except Exception as e:
        print(f"Error in TTS synthesis: {e}")
        return b""
