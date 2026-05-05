import langdetect

def detect_language(text: str) -> str:
    """
    Detects language from text. Maps to English, Hindi, or Tamil.
    Falls back to English if unsure.
    """
    try:
        code = langdetect.detect(text)
        if code in ['hi', 'mr', 'ne']:
            return "Hindi"
        elif code == 'ta':
            return "Tamil"
        elif code == 'en':
            return "English"
        else:
            return "English"
    except:
        return "English"
