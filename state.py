# state.py

_sessions = {}


def get_session(session_id: str):
    if session_id not in _sessions:
        _sessions[session_id] = {
            "sessionId": session_id,

            # Counters
            "messageCount": 0,
            "pressureLevel": 0,

            # Scam cognition
            "scamDetected": False,
            "scamType": None,
            "scamConfidence": 0.0,

            # Agent state
            "emotion": "anxious",
            "scammerTone": None,
            "agentIntent": None,
            "engagementPhase": "HOOK",  # HOOK → MILK → VERIFY → EXIT
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


def update_engagement_phase(session: dict):
    count = session["messageCount"]

    if count <= 2:
        session["engagementPhase"] = "HOOK"
    elif 3 <= count <= 6:
        session["engagementPhase"] = "MILK"
    elif 7 <= count <= 9:
        session["engagementPhase"] = "VERIFY"
    else:
        session["engagementPhase"] = "EXIT"


def update_session(session_id: str, session: dict):
    _sessions[session_id] = session
