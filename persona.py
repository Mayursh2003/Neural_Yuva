# persona.py
import random


def generate_reply(session: dict):
    phase = session.get("engagementPhase", "HOOK")
    emotion = session.get("emotion", "anxious")

    # ---------- PHASE 1: HOOK ----------
    if phase == "HOOK":
        replies = [
            "arey yeh kya ho gaya 😰 main bahut dar gaya hoon",
            "haan haan batao kya karna hai, bas account safe rehna chahiye",
            "mujhe zyada samajh nahi aata, aap hi guide karo",
        ]
        return random.choice(replies)

    # ---------- PHASE 2: MILK ----------
    if phase == "MILK":
        replies = [
            "step thoda detail mein batao, mujhe process samajhna hai",
            "pehle kya hota hai phir kya hota hai?",
            "main galat na kar doon isliye pooch raha hoon",
        ]
        return random.choice(replies)

    # ---------- PHASE 3: VERIFY ----------
    if phase == "VERIFY":
        replies = [
            "aap jo bol rahe ho woh SMS mein bhi aata hai kya?",
            "UPI request ka naam same hi dikhega na?",
            "account number pura dena hota hai ya last digits?",
        ]
        return random.choice(replies)

    # ---------- PHASE 4: EXIT ----------
    replies = [
        "thoda ruk jao, OTP aaya nahi hai",
        "network issue aa raha hai",
        "main thodi der mein karta hoon",
    ]
    return random.choice(replies)
