# emotion.py

def update_emotion(session: dict, text: str):
    confidence = session.get("scamConfidence", 0.0)
    current = session["emotion"]

    if confidence >= 0.3 and current == "neutral":
        session["emotion"] = "confused"

    elif confidence >= 0.6 and current in ["neutral", "confused"]:
        session["emotion"] = "anxious"

    elif confidence >= 0.85:
        session["emotion"] = "distressed"
