from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Union

from state import get_session, update_session, choose_agent_intent
from detection import detect_scam
from tone import detect_tone
from emotion import update_emotion
from persona import generate_reply
from extraction import extract_intelligence
from callback import send_final_callback
from llm_advisor import llm_classify




# 🔴 THIS MUST COME BEFORE @app.post
app = FastAPI()


class Message(BaseModel):
    sender: str
    text: str
    timestamp: Optional[int] = None  # epoch ms

class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None

class RequestBody(BaseModel):
    sessionId: str
    message: Union[str, Message]
    conversationHistory: List[Message] = Field(default_factory=list)
    metadata: Optional[Metadata] = None

    @model_validator(mode="after")
    def normalize_message(self):
        if isinstance(self.message, str):
            self.message = Message(sender="scammer", text=self.message)
        return self


@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.post("/honeypot/message")
def honeypot(
    body: RequestBody,
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):

    if not x_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if isinstance(body.message, str):
        body.message = Message(
        sender="scammer",
        text=body.message
    )

     


    session = get_session(body.sessionId)
    session["messageCount"] += 1

    text = body.message.text

    # 1. Scam detection
    scam_detected, scam_type = detect_scam(text, session)
    if scam_detected:
        session["scamDetected"] = True
        session["scamType"] = scam_type

    # 2. LLM assist (SAFE)
    # LLM assist
    llm_result = None
    if (
    session["scamType"] in [None, "GENERIC_SCAM"]
    and 0.3 <= session["scamConfidence"] <= 0.6
    ):
     llm_result = llm_classify(text)

    if llm_result:
        session["scamType"] = llm_result.get("scam_archetype")
        session["agentIntent"] = llm_result.get("suggested_intent")

    # intent fallback
    if not session.get("agentIntent"):
        session["agentIntent"] = choose_agent_intent(session)


    # 3. Tone + emotion
    session["scammerTone"] = detect_tone(text)
    update_emotion(session, text)

    # 4. Intelligence extraction
    extract_intelligence(session, text)

    # 5. Intent selection (only if not set)
    if not session.get("agentIntent"):
        session["agentIntent"] = choose_agent_intent(session)
    #  Refund-scam steering: once UPI is mentioned, stay on destination
    lower = text.lower()
    if (
    session.get("scamType") == "REFUND_SCAM"
    and any(k in lower for k in ["upi", "phonepe", "gpay", "paytm", "request"])
    ):
        session["agentIntent"] = "VERIFY_DESTINATION"

    # 6. Completion logic
    if (
        session["scamConfidence"] >= 0.9 and (
            session["extractedIntelligence"]["upiIds"] or
            session["extractedIntelligence"]["phishingLinks"]
        )
    ):
        if not session.get("conversationComplete"):
            session["conversationComplete"] = True
            send_final_callback(session)

        reply = "main samajh nahi pa raha\nthoda ruk jao"
    else:
        reply = generate_reply(session)

    update_session(body.sessionId, session)

    return {
        "status": "success",
        "reply": reply
    }
