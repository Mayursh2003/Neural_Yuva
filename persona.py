# persona.py
import random

USED_REPLIES = set()

INTENT_TEMPLATES = {
    "VERIFY_PROCESS": [
        "bank ka process usually SMS ya call se aata hai na?",
        "agar account issue hai toh official message aana chahiye",
        "main galti nahi karna chahta, process thoda odd lag raha hai"
    ],

    "VERIFY_IDENTITY": [
        "aap kaunse branch se bol rahe ho?",
        "aapka employee ID ya extension number kya hai?",
        "main bank ke number par callback kar sakta hoon?"
    ],

    "VERIFY_DESTINATION": [
        "jo UPI aap bol rahe ho uska naam kya show hota hai?",
        "receive aur pay mein difference hota hai na?",
        "main pehle check kar leta hoon, accept baad mein karunga"
    ],

    "VERIFY_PAYMENT_MODE": [
        "lottery ka paisa direct UPI se aata hai kya?",
        "koi official mail ya letter hota hoga na?",
        "main pehle confirm karna chahta hoon"
    ]
}

EMOTION_MODIFIERS = {
    "confused": [
        "mujhe thoda doubt ho raha hai",
        "clear nahi lag raha honestly"
    ],
    "anxious": [
        "kahin paisa na phas jaye",
        "pehle bhi fraud hua hai mere saath"
    ],
    "fearful": [
        "account block ho gaya toh badi problem ho jayegi",
        "ghar wale mana kar rahe hain"
    ]
}


def generate_reply(session: dict):
    intent = session.get("agentIntent", "VERIFY_PROCESS")
    emotion = session.get("emotion", "confused")

    templates = INTENT_TEMPLATES.get(intent, ["thoda ruk jao"])
    modifiers = EMOTION_MODIFIERS.get(emotion, [""])

    # prevent repetition
    for _ in range(5):
        base = random.choice(templates)
        modifier = random.choice(modifiers)
        reply = base
        if modifier:
            reply = reply + ", " + modifier
        if reply not in USED_REPLIES:
            USED_REPLIES.add(reply)
            return reply

    return "main thoda busy hoon, baad mein baat karte hain"
