# persona.py
import random

USED_REPLIES = set()


def generate_reply(session: dict):
    phase = session.get("engagementPhase", "HOOK")

    # ---------- HOOK ----------
    if phase == "HOOK":
        replies = [
            "arey yeh kya ho gaya maine to kuch kiya he nahi",
            "ese kese",
            "kese karna hai btao jaldi se",
        ]

    # ---------- MILK ----------
    elif phase == "MILK":
        replies = [
            "step thoda detail mein batao, pehle kya karna hai?",
            "main galat na kar doon isliye pooch raha hoon",
            "aap jaise bol rahe ho waise hi karna hai na?"
        ]

    # ---------- VERIFY ----------
    elif phase == "VERIFY":
        replies = [
            "UPI yhi h  kya?",
            "account number pura dena hota hai ya last digits?",
            "OTP aane ke baad next kya hota hai?"
        ]

    # ---------- EXIT ----------
    else:
        replies = [
            "OTP aaya nahi hai, thoda ruk jao",
            "network slow hai, 2 minute do",
            "main thodi der mein karta hoon"
        ]

    for _ in range(5):
        reply = random.choice(replies)
        if reply not in USED_REPLIES:
            USED_REPLIES.add(reply)
            return reply

    return "ruko main dekhta hoon"  # fallback reply
