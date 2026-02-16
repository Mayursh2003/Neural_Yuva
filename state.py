# state.py

_sessions = {}


def get_session(session_id: str):
    """
    Initialize or return an existing session.
    This function MUST remain stable to avoid breaking API behavior.
    """
    if session_id not in _sessions:
        _sessions[session_id] = {
            "sessionId": session_id,

            # ---- Counters ----
            "messageCount": 0,
            "pressureLevel": 0,

            # ---- Scam cognition ----
            "scamDetected": False,
            "scamType": None,
            "scamConfidence": 0.0,

            # ---- Agent state ----
            "emotion": "anxious",
            "scammerTone": None,
            "agentIntent": None,
            "engagementPhase": "HOOK",  # HOOK → MILK → VERIFY → EXIT
            "conversationComplete": False,

            # ---- Intelligence store ----
            "extractedIntelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            },

            # ---- Internal logs (for dataset later, NOT sent to API) ----
            "internalLog": []  # each entry = {"turn": n, "text": "..."}
        }

    return _sessions[session_id]


def update_engagement_phase(session: dict):
    """
    Controls how human-like the conversation feels.
    Do NOT change thresholds unless you know why.
    """
    count = session.get("messageCount", 0)

    if count <= 2:
        session["engagementPhase"] = "HOOK"
    elif 3 <= count <= 6:
        session["engagementPhase"] = "MILK"
    elif 7 <= count <= 9:
        session["engagementPhase"] = "VERIFY"
    else:
        session["engagementPhase"] = "EXIT"


def update_pressure(session: dict, text: str):
    """
    Pressure increases when scammer uses urgency/threat language.
    This indirectly affects emotion.
    """
    lower = text.lower()

    triggers = [
        "urgent", "immediately", "blocked", "suspend",
        "last chance", "verify now", "otp", "pin",
        "account will be blocked", "time left"
    ]

    if any(t in lower for t in triggers):
        session["pressureLevel"] += 1

    session["pressureLevel"] = min(session["pressureLevel"], 5)


def update_emotion_from_pressure(session: dict):
    """
    Maps pressure to human emotion.
    Simple, explainable, predictable.
    """
    p = session.get("pressureLevel", 0)

    if p <= 1:
        session["emotion"] = "confused"
    elif p <= 3:
        session["emotion"] = "anxious"
    else:
        session["emotion"] = "fearful"


def update_scam_confidence(session: dict):
    """
    Gradual confidence increase.
    Avoids early hard decisions.
    """
    if session.get("scamDetected"):
        session["scamConfidence"] = min(
            1.0,
            session.get("scamConfidence", 0.0) + 0.12
        )


def log_message(session: dict, text: str):
    """
    Internal logging only.
    Safe for demo.
    Useful for dataset creation later.
    """
    session["internalLog"].append({
        "turn": session.get("messageCount", 0),
        "text": text
    })


def update_session(session_id: str, session: dict):
    """
    Persist session state.
    """
    _sessions[session_id] = session