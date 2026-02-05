# emotion.py

def update_emotion(session: dict, text: str):
    lower = text.lower()

    if any(w in lower for w in ["urgent", "blocked", "immediately", "last chance"]):
        session["pressureLevel"] += 1

    if session["pressureLevel"] <= 1:
        session["emotion"] = "confused"
    elif session["pressureLevel"] == 2:
        session["emotion"] = "anxious"
    elif session["pressureLevel"] >= 3:
        session["emotion"] = "fearful"

