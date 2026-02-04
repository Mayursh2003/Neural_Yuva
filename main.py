from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from state import get_session, update_session, choose_agent_intent
from detection import detect_scam
from tone import detect_tone
from emotion import update_emotion
from persona import generate_reply
from extraction import extract_intelligence
from callback import send_final_callback
from llm_advisor import llm_classify

app = FastAPI()


# --------- MODELS (MATCH GUVI EXACTLY) ---------

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int  # epoch ms (IMPORTANT)


class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None


class RequestBody(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message]
    metadata: Optional[Metadata] = None


# --------- HEALTH CHECK ---------

@app.get("/healthz")
def health():
    return {"status": "ok"}


# --------- MAIN ENDPOINT ---------

@app.post("/honeypot/message")
def honeypot(body: RequestBody, x_api_key: Optional[str] = Header(None)):

    if not x_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session = get_session(body.sessionId)
    session["messageCount"] += 1

    text = body.message.text.lower()

    # 1. Scam detection
    scam_detected, scam_type = detect_scam(text, session)
    if scam_detected:
        session["scamDetected"] = True
        session["scamType"] = scam_type

    # 2. Optional LLM assist (only mid-confidence)
    if session["scamType"] in [None, "GENERIC_SCAM"] and 0.3 <= session["scamConfidence"] <= 0.6:
        llm_result = llm_classify(text)
        if llm_result:
            session["scamType"] = llm_result.get("scam_archetype")
            session["agentIntent"] = llm_result.get("suggested_intent")

    # 3. Intent fallback
    if not session.get("agentIntent"):
        session["agentIntent"] = choose_agent_intent(session)

    # 4. Tone & emotion
    session["scammerTone"] = detect_tone(text)
    update_emotion(session, text)

    # 5. Intelligence extraction
    extract_intelligence(session, text)

    # 6. Completion + callback
    if (
        session["scamConfidence"] >= 0.9 and (
            session["extractedIntelligence"]["upiIds"] or
            session["extractedIntelligence"]["phishingLinks"]
        )
    ):
        if not session.get("conversationComplete"):
            session["conversationComplete"] = True
            send_final_callback(session)

        reply = "thoda samajh nahi aa raha… thoda time do"
    else:
        reply = generate_reply(session)

    update_session(body.sessionId, session)

    return {
        "status": "success",
        "reply": reply
    }
