
from fastapi import FastAPI, Header, HTTPException, Request
from typing import Optional

from state import get_session, update_session, choose_agent_intent
from detection import detect_scam
from tone import detect_tone
from emotion import update_emotion
from persona import generate_reply
from extraction import extract_intelligence
from callback import send_final_callback
from llm_advisor import llm_classify

app = FastAPI()


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/honeypot/message")
async def honeypot(request: Request, x_api_key: Optional[str] = Header(None)):

    if not x_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ---- RAW BODY (NO PYDANTIC) ----
    try:
        body = await request.json()
    except Exception:
        body = {}

    session_id = body.get("sessionId", "unknown-session")

    raw_message = body.get("message", "")
    conversation = body.get("conversationHistory", [])

    # ---- NORMALIZE MESSAGE ----
    if isinstance(raw_message, dict):
        text = str(raw_message.get("text", ""))
    elif isinstance(raw_message, str):
        text = raw_message
    else:
        text = ""

    text = text.strip()

    # ---- SESSION ----
    session = get_session(session_id)
    session["messageCount"] += 1

    # ---- SCAM DETECTION ----
    scam_detected, scam_type = detect_scam(text, session)
    if scam_detected:
        session["scamDetected"] = True
        session["scamType"] = scam_type

    # ---- OPTIONAL LLM ASSIST ----
    if session["scamType"] in [None, "GENERIC_SCAM"] and 0.3 <= session["scamConfidence"] <= 0.6:
        llm_result = llm_classify(text)
        if llm_result:
            session["scamType"] = llm_result.get("scam_archetype")
            session["agentIntent"] = llm_result.get("suggested_intent")

    if not session.get("agentIntent"):
        session["agentIntent"] = choose_agent_intent(session)

    # ---- TONE & EMOTION ----
    session["scammerTone"] = detect_tone(text)
    update_emotion(session, text)

    # ---- INTELLIGENCE EXTRACTION ----
    extract_intelligence(session, text)

    # ---- FINAL CALLBACK ----
    if (
        session["scamConfidence"] >= 0.9 and
        (session["extractedIntelligence"]["upiIds"] or session["extractedIntelligence"]["phishingLinks"])
    ):
        if not session.get("conversationComplete"):
            session["conversationComplete"] = True
            send_final_callback(session)

        reply = "thoda samajh nahi aa raha… thoda time do"
    else:
        reply = generate_reply(session)

    update_session(session_id, session)

    return {
        "status": "success",
        "reply": reply
    }
