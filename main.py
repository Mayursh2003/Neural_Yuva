from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import time

from state import (
    get_session,
    update_session,
    update_engagement_phase,
    update_pressure,
    update_emotion_from_pressure,
    update_scam_confidence,
    log_message
)

from detection import detect_scam
from tone import detect_tone
from persona import generate_reply
from extraction import extract_intelligence
from callback import send_final_callback
from llm_advisor import llm_classify

app = FastAPI()


# ---------------- MODELS (GUVI SAFE) ----------------

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


# ---------------- MAIN ENDPOINT ----------------

@app.post("/honeypot/message")
async def honeypot(
    body: RequestBody,
    request: Request,
    x_api_key: Optional[str] = Header(None)
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session = get_session(body.sessionId)

    # ---- increment turn count ----
    session["messageCount"] += 1

    # ---- update conversation phase ----
    update_engagement_phase(session)

    # ---- normalize incoming message ----
    msg = body.message or {}
    text = msg.get("text", "")
    sender = msg.get("sender", "scammer")

    if not isinstance(text, str):
        text = str(text)

    # ---- internal logging (dataset safe) ----
    log_message(session, text)

    # ---- scam detection (cheap + deterministic first) ----
    scam_detected, scam_type = detect_scam(text, session)
    if scam_detected:
        session["scamDetected"] = True
        session["scamType"] = scam_type

    # ---- pressure + emotion ----
    update_pressure(session, text)
    update_emotion_from_pressure(session)
    update_scam_confidence(session)

    # ---- tone (informational only) ----
    session["scammerTone"] = detect_tone(text)

    # ---- intelligence extraction (always run) ----
    extract_intelligence(session, text)

    # ---- LLM assist (STRICTLY bounded) ----
    # LLM is advisory only, never controls flow
    if (
        session["scamType"] in [None, "GENERIC_SCAM"]
        and 0.35 <= session["scamConfidence"] <= 0.65
        and session["engagementPhase"] in ["MILK", "VERIFY"]
    ):
        llm_result = llm_classify(text)
        if llm_result:
            session["scamType"] = llm_result.get(
                "scam_archetype", session["scamType"]
            )

    # ---- completion logic (GUVI-safe) ----
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

    # ---- generate reply (human pacing) ----
    reply = generate_reply(session)

    # ---- persist session ----
    update_session(body.sessionId, session)

    return {
        "status": "success",
        "reply": reply
    }