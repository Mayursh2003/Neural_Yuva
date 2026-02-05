# tone.py

def detect_tone(text: str):
    t = text.lower()

    if "immediately" in t or "now" in t or "fast" in t:
        return "rushed"

    if "blocked" in t or "suspended" in t:
        return "aggressive"

    if len(text.split()) <= 3:
        return "sloppy"
    

    if any(w in t for w in ["urgent", "immediately", "blocked", "last chance"]):
        return "threatening"

    if any(w in t for w in ["sir", "madam", "trust", "verify"]):
        return "authoritative"

    return "neutral"

    return "formal"

