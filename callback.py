# callback.py
import requests

GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

def send_final_callback(session: dict):
    payload = {
        "sessionId": session["sessionId"],
        "scamDetected": session["scamDetected"],
        "totalMessagesExchanged": session["messageCount"],
        "extractedIntelligence": session["extractedIntelligence"],
        "agentNotes": "Scammer used urgency and account blocking tactics"
    }

    try:
        requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
    except Exception:
        # silent fail by design (as per problem statement)
        pass
