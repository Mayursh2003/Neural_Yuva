from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from state import (
    get_session,
    update_session,
    update_engagement_phase,
)

from detection import detect_scam
from tone import detect_tone
from persona import generate_reply
from extraction import extract_intelligence
from callback import send_final_callback

app = FastAPI()


# ---------- MODELS (GUVI COMPATIBLE) ----------

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

    # 🔥 engagement phase update
    update_engagement_phase(session)

    # normalize message
    msg = body.message or {}
    text = msg.get("text", "")
    if not isinstance(text, str):
        text = str(text)

    # scam detection
    scam_detected, scam_type = detect_scam(text, session)
    if scam_detected:
        session["scamDetected"] = True
        session["scamType"] = scam_type
        session["scamConfidence"] = min(1.0, session["scamConfidence"] + 0.15)

    # tone
    session["scammerTone"] = detect_tone(text)

    # intelligence extraction (NOW WORKS)
    extract_intelligence(session, text)

    # 🎯 intent logic STRICTLY by phase
    phase = session["engagementPhase"]

    if phase in ["HOOK", "MILK"]:
        session["agentIntent"] = "VERIFY_PROCESS"

    elif phase == "VERIFY":
        if session.get("scamType") == "REFUND_SCAM":
            session["agentIntent"] = "VERIFY_DESTINATION"
        else:
            session["agentIntent"] = "VERIFY_IDENTITY"

    # completion + callback
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
