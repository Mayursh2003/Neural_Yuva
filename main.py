
from fastapi import FastAPI, Header, HTTPException, Request
from typing import Optional
import json
import logging

from state import get_session, update_session, choose_agent_intent
from detection import detect_scam
from tone import detect_tone
from emotion import update_emotion
from persona import generate_reply
from extraction import extract_intelligence
from callback import send_final_callback
from llm_advisor import llm_classify


app = FastAPI()



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("guvi-debug")


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/honeypot/message")
async def honeypot(request: Request, x_api_key: Optional[str] = Header(None)):

    if not x_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ---- RAW REQUEST LOGGING ----
    try:
        raw_body = await request.body()
        raw_text = raw_body.decode("utf-8", errors="ignore")
        body = json.loads(raw_text) if raw_text else {}
    except Exception as e:
        logger.error(f"Failed to parse JSON body: {e}")
        body = {}
        raw_text = ""

    logger.info("===== GUVI REQUEST RECEIVED =====")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Raw body: {raw_text}")
    logger.info("=================================")

    # ---- NORMALIZATION ----
    session_id = body.get("sessionId", "unknown-session")
    raw_message = body.get("message", "")
    conversation = body.get("conversationHistory", [])

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

        reply = "thoda samajh nahi aa raha… thoda ruk jao"
    else:
        reply = generate_reply(session)

    update_session(session_id, session)

    return {
        "status": "success",
        "reply": reply
    }
