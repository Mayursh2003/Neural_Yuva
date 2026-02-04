# llm_advisor.py
import os
import requests
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)


def _clean_json(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Invalid JSON from LLM")

    return json.loads(text[start:end + 1])


def llm_classify(message_text: str):
    if not GEMINI_API_KEY:
        return None

    prompt = f"""
You are classifying scam intent in India.
You are NOT chatting with a scammer.

Message:
"{message_text}"

Return ONLY valid JSON:
{{
  "scam_archetype": "...",
  "dominant_psychology": "...",
  "suggested_intent": "...",
  "confidence": "low|medium|high"
}}

Possible scam_archetype:
THREAT_SCAM, LOTTERY_SCAM, REFUND_SCAM, AUTHORITY_SCAM, JOB_SCAM, GENERIC_SCAM

Possible suggested_intent:
VERIFY_PROCESS, VERIFY_DESTINATION, VERIFY_PAYMENT_MODE, VERIFY_IDENTITY
"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        r = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=5
        )
        raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return _clean_json(raw)
    except Exception:
        return None
