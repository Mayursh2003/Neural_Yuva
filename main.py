from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from requests import session

from state import get_session, update_session, choose_agent_intent
from detection import detect_scam
from tone import detect_tone
from emotion import update_emotion
from persona import generate_reply
from extraction import extract_intelligence
from callback import send_final_callback
from llm_advisor import llm_classify

app = FastAPI()


# ---------- MODELS (GUVI-COMPATIBLE) ----------

class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None


class RequestBody(BaseModel):
    sessionId: str
    message: Dict[str, Any]
    conversationHistory: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Optional[Metadata] = None


@app.get("/healthz")
def health():
    return {"status": "ok"}


# ---------- MAIN ENDPOINT ----------

@app.post("/honeypot/message")
async def honeypot(
    body: RequestBody,
    request: Request,
    x_api_key: Optional[str] = Header(None)
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session = get_session(body.sessionId)
    session["messageCount"] += 1

    # ---- normalize incoming message ----
    msg = body.message or {}
    text = msg.get("text", "")
    sender = msg.get("sender", "scammer")

    if not isinstance(text, str):
        text = str(text)

    # ---- scam detection ----
    scam_detected, scam_type = detect_scam(text, session)
    if scam_detected:
        session["scamDetected"] = True
        session["scamType"] = scam_type

    # ---- tone + emotion ----
    session["scammerTone"] = detect_tone(text)
    update_emotion(session, text)

    # ---- intelligence extraction ----
    extract_intelligence(session, text)

    # ---- LLM assist (only mid-confidence) ----
    if (
        session["scamType"] in [None, "GENERIC_SCAM"]
        and 0.3 <= session["scamConfidence"] <= 0.6
    ):
        llm = llm_classify(text)
        if llm:
            session["scamType"] = llm.get("scam_archetype", session["scamType"])
            session["agentIntent"] = llm.get("suggested_intent")

    # ---- choose intent ----
    session["agentIntent"] = choose_agent_intent(session)

    # --- intent escalation if scammer repeats same demand ---
    if session["messageCount"] >= 3:
        if session["agentIntent"] == "VERIFY_PROCESS":
            session["agentIntent"] = "VERIFY_IDENTITY"
        elif session["agentIntent"] == "VERIFY_IDENTITY":
            session["agentIntent"] = "VERIFY_DESTINATION"


    # ---- completion + callback ----
    if (
        session["scamDetected"]
        and session["scamConfidence"] >= 0.85
        and (
            session["extractedIntelligence"]["upiIds"]
            or session["extractedIntelligence"]["phoneNumbers"]
            or session["extractedIntelligence"]["bankAccounts"]
        )
    ):
        if not session.get("conversationComplete"):
            session["conversationComplete"] = True
            send_final_callback(session)

    # ---- agent reply ----
    reply = generate_reply(session)

    update_session(body.sessionId, session)

    return {
        "status": "success",
        "reply": reply
    }
