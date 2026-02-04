# persona.py
import random

INTENT_TEMPLATES = {
    "VERIFY_PROCESS": [
        "achha, process kya hai",
        "thoda detail mein batao",
        "next step kya hoga"
    ],

    "VERIFY_DESTINATION": [
        "kis account mein bhejna hai",
        "kaun sa account hai jahan wapas bhejna hai",
        "details bhejo, main check karta hoon"
    ],

    "VERIFY_PAYMENT_MODE": [
        "upi se hoga ya bank transfer",
        "link bhejni padegi kya",
        "paytm ya gpay chalega"
    ],

    "VERIFY_IDENTITY": [
        "aap kaun bol rahe ho exactly",
        "bank kaunse branch se ho",
        "koi ID ya reference hai"
    ]
}

EMOTION_MODIFIERS = {
    "neutral": [""],
    "confused": [
        " mujhe thoda clear nahi hai",
        " samajh nahi aa raha properly"
    ],
    "anxious": [
        " thoda soch samajh ke karna padega",
        " galti ho gayi toh dikkat ho jayegi"
    ],
    "distressed": [
        " paisa zyada amount hai",
        " ghar walon se poochna padega"
    ]
}


def generate_reply(session: dict):
    intent = session.get("agentIntent") or "VERIFY_PROCESS"
    emotion = session.get("emotion", "neutral")

    templates = INTENT_TEMPLATES.get(intent)
    if not templates:
        templates = ["samajhne do, phir se batao"]

    base = random.choice(templates)

    # hesitation without duplication
    if random.random() < 0.3 and not base.startswith("achha"):
        base = "achha… " + base

    modifier = ""
    if session.get("messageCount", 0) > 1:
        modifier = random.choice(
            EMOTION_MODIFIERS.get(emotion, [""])
        )

    reply = base
    if modifier:
        reply = reply + ", " + modifier.lstrip()


    # absolute safety fallback
    if not reply:
        reply = "thoda ruk jao, main samajh raha hoon"

    return reply
