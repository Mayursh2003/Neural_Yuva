# state.py

_sessions = {}


def init_session(session_id):
    return {
        "sessionId": session_id,
        "emotion": "neutral",
        "scamDetected": False,
        "scamConfidence": 0.0,
        "scamType": None,
        "agentIntent": None,
        "messageCount": 0,
        "extractedIntelligence": {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }
    }


def get_session(session_id: str):
    if session_id not in _sessions:
        _sessions[session_id] = {
            "sessionId": session_id,
            "messageCount": 0,

            # Scam cognition
            "scamDetected": False,
            "scamType": None,
            "scamConfidence": 0.0,   # 👈 key addition

            # Behavior
            "scammerTone": None,
            "emotion": "neutral",
            "conversationComplete": False,

            # Intelligence
            "extractedIntelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            }
        }
    return _sessions[session_id]

def choose_agent_intent(session):
    if session.get("agentIntent"):
        return session["agentIntent"]

    c = session.get("scamConfidence", 0)
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
