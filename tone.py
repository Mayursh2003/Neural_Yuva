# tone.py

def detect_tone(text: str):
    t = text.lower()

    if "immediately" in t or "now" in t or "fast" in t:
        return "rushed"

    if "blocked" in t or "suspended" in t:
        return "aggressive"

    if len(text.split()) <= 3:
        return "sloppy"

    return "formal"

