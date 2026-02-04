from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Union, Dict, Any

from state import get_session, update_session, choose_agent_intent
from detection import detect_scam
from tone import detect_tone
from emotion import update_emotion
from persona import generate_reply
from extraction import extract_intelligence
from callback import send_final_callback
from llm_advisor import llm_classify
from typing import Optional, List, Union, Dict, Any
import uuid


app = FastAPI()


# ---------- MODELS ----------

class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None


class Message(BaseModel):
    sender: str
    text: str
    timestamp: Optional[int] = None  # epoch ms


class RequestBody(BaseModel):
    sessionId: Optional[str] = None
    message: Optional[Union[str, Dict[str, Any], Message]] = None
    conversationHistory: Optional[List[Message]] = None
    metadata: Optional[Dict[str, Any]] = None



# ---------- HEALTH ----------

@app.get("/healthz")
def health():
    return {"status": "ok"}


# ---------- MAIN ENDPOINT ----------

@app.post("/honeypot/message")
def honeypot(body: RequestBody, x_api_key: Optional[str] = Header(None)):

    if not x_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ---- Session ID handling (GUVI tester safe) ----
    session_id = body.sessionId or f"auto-{uuid.uuid4().hex[:12]}"
    session = get_session(session_id)
    session["messageCount"] += 1

    # ---- Message normalization (VERY IMPORTANT) ----
    if body.message is None:
        raise HTTPException(status_code=400, detail="Message is required")

    if isinstance(body.message, str):
        message = Message(sender="scammer", text=body.message)

    elif isinstance(body.message, dict):
        message = Message(
            sender=body.message.get("sender", "scammer"),
            text=body.message.get("text", ""),
            timestamp=body.message.get("timestamp")
        )

    elif isinstance(body.message, Message):
        message = body.message

    else:
        raise HTTPException(status_code=400, detail="Invalid message format")

    text = message.text.lower()


    # 1️⃣ Scam detection (rule-based)
    scam_detected, scam_type = detect_scam(text, session)
    if scam_detected:
        session["scamDetected"] = True
        session["scamType"] = scam_type

    # 2️⃣ LLM assist (only mid-confidence ambiguity)
    llm_result = None
    if (
        session["scamType"] in [None, "GENERIC_SCAM"]
        and 0.3 <= session["scamConfidence"] <= 0.6
    ):
        llm_result = llm_classify(text)

    if llm_result:
        session["scamType"] = llm_result.get("scam_archetype", session["scamType"])
        session["agentIntent"] = llm_result.get("suggested_intent")

    # 3️⃣ Intent fallback
    if not session.get("agentIntent"):
        session["agentIntent"] = choose_agent_intent(session)

    # 4️⃣ Tone + emotion
    session["scammerTone"] = detect_tone(text)
    update_emotion(session, text)

    # 5️⃣ Intelligence extraction
    extract_intelligence(session, text)

    # Refund-scam steering
    if (
        session["scamType"] == "REFUND_SCAM"
        and any(k in text for k in ["upi", "phonepe", "gpay", "paytm", "request"])
    ):
        session["agentIntent"] = "VERIFY_DESTINATION"

    # 6️⃣ Completion logic
    if (
        session["scamConfidence"] >= 0.9
        and (
            session["extractedIntelligence"]["upiIds"]
            or session["extractedIntelligence"]["phishingLinks"]
        )
    ):
        if not session.get("conversationComplete"):
            session["conversationComplete"] = True
            send_final_callback(session)

        reply = "main thoda confused ho gaya hoon, thoda ruk jao"
    else:
        reply = generate_reply(session)

    update_session(body.sessionId, session)

    return {
        "status": "success",
        "reply": reply
    }
