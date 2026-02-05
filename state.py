# state.py

_sessions = {}


def get_session(session_id: str):
    if session_id not in _sessions:
        _sessions[session_id] = {
            "sessionId": session_id,

            # Counters
            "messageCount": 0,
            "pressureLevel": 0,   # increases with scammer urgency

            # Scam cognition
            "scamDetected": False,
            "scamType": None,
            "scamConfidence": 0.0,

            # Agent state
            "emotion": "confused",
            "scammerTone": None,
            "agentIntent": None,
            "conversationComplete": False,

            # Intelligence store
            "extractedIntelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            }
        }

    return _sessions[session_id]


def update_pressure(session: dict, text: str):
    """Increase pressure based on urgency / threat language"""
    lower = text.lower()

    triggers = [
        "urgent", "immediately", "blocked", "suspend",
        "last chance", "verify now", "otp", "pin"
    ]

    if any(k in lower for k in triggers):
        session["pressureLevel"] += 1

    # cap it
    session["pressureLevel"] = min(session["pressureLevel"], 5)


def update_emotion_from_pressure(session: dict):
    """Map pressure → emotion"""
    p = session.get("pressureLevel", 0)

    if p <= 1:
        session["emotion"] = "confused"
    elif p <= 3:
        session["emotion"] = "anxious"
    else:
        session["emotion"] = "fearful"


def update_scam_confidence(session: dict):
    """Accumulate confidence across turns"""
    if session.get("scamDetected"):
        session["scamConfidence"] = min(
            1.0,
            session.get("scamConfidence", 0) + 0.15
        )


def choose_agent_intent(session: dict):
    """
    Decide what the agent should probe NEXT
    """

    # Preserve intent once chosen (agent consistency)
    if session.get("agentIntent"):
        return session["agentIntent"]

    c = session.get("scamConfidence", 0.0)
    t = session.get("scamType")

    if c < 0.4:
        return "VERIFY_PROCESS"

    if t in ["THREAT_SCAM", "AUTHORITY_SCAM"]:
        return "VERIFY_IDENTITY"

    if t in ["LOTTERY_SCAM", "JOB_SCAM"]:
        return "VERIFY_PAYMENT_MODE"

    if t == "REFUND_SCAM":
        return "VERIFY_DESTINATION"

    return "VERIFY_PROCESS"


def update_session(session_id: str, session: dict):
    _sessions[session_id] = session
