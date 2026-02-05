# state.py

_sessions = {}


def get_session(session_id: str):
    if session_id not in _sessions:
        _sessions[session_id] = {
            "sessionId": session_id,

            "messageCount": 0,

            # NEW: track if victim seems cooperative
            "softCompliance": 0,   # 0 → 3

            "scamDetected": False,
            "scamType": None,
            "scamConfidence": 0.0,

            "emotion": "anxious",
            "scammerTone": None,
            "agentIntent": None,

            "engagementPhase": "HOOK",  # HOOK → MILK → VERIFY → EXIT
            "conversationComplete": False,

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
    mc = session["messageCount"]

    if mc <= 2:
        session["engagementPhase"] = "HOOK"
    elif mc <= 6:
        session["engagementPhase"] = "MILK"
    elif mc <= 9:
        session["engagementPhase"] = "VERIFY"
    else:
        session["engagementPhase"] = "EXIT"


def update_session(session_id: str, session: dict):
    _sessions[session_id] = session
