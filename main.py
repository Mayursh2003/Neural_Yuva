from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from state import (
    get_session,
    update_session,
    update_engagement_phase,
    choose_agent_intent
)

from detection import detect_scam
from tone import detect_tone
from persona import generate_reply
from extraction import extract_intelligence
from callback import send_final_callback

app = FastAPI()


# ---------- MODELS ----------

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

    # Engagement phase
    update_engagement_phase(session)

    # Normalize text
    msg = body.message or {}
    text = msg.get("text", "")
    if not isinstance(text, str):
        text = str(text)

    # Scam detection
    scam_detected, scam_type = detect_scam(text, session)
    if scam_detected:
        session["scamDetected"] = True
        session["scamType"] = scam_type
        session["scamConfidence"] = min(
            1.0, session.get("scamConfidence", 0.0) + 0.15
        )

    # Tone
    session["scammerTone"] = detect_tone(text)

    # Intelligence extraction
    extract_intelligence(session, text)

    # Intent strictly by phase
    session["agentIntent"] = choose_agent_intent(session)

    # Completion + callback
    if (
        session["scamDetected"]
        and session["scamConfidence"] >= 0.85
        and (
            session["extractedIntelligence"]["upiIds"]
            or session["extractedIntelligence"]["phoneNumbers"]
            or session["extractedIntelligence"]["bankAccounts"]
        )
        and not session["conversationComplete"]
    ):
        session["conversationComplete"] = True
        send_final_callback(session)

    reply = generate_reply(session)

    update_session(body.sessionId, session)

    return {
        "status": "success",
        "reply": reply
    }
