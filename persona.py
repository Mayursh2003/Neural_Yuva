# persona.py
import random


def generate_reply(session: dict):
    phase = session.get("engagementPhase", "HOOK")

    # ---------- HOOK: fear + obedience ----------
    if phase == "HOOK":
        return random.choice([
            "arey yeh kya ho gaya 😰 haan haan batao kya karna hai",
            "please jaldi batao, account block ho gaya toh problem ho jayegi",
            "mujhe zyada samajh nahi aata, aap jaise bolo waise karunga"
        ])

    # ---------- MILK: PARTIAL COMPLIANCE (CRITICAL) ----------
    if phase == "MILK":
        session["softCompliance"] = min(3, session.get("softCompliance", 0) + 1)

        return random.choice([
            "achha… account number ready kar raha hoon, pehle confirm kar loon",
            "OTP aane hi wala hai, bas ek baar process samjha do",
            "haan samajh aa raha hai, pehle kya dalna hota hai?"
        ])

    # ---------- VERIFY: SOFT confirmation, not challenge ----------
    if phase == "VERIFY":
        return random.choice([
            "UPI request aap bhejoge ya mujhe type karna hoga?",
            "account number pura dalna hota hai ya last digits?",
            "OTP ke baad koi aur step toh nahi hota na?"
        ])

    # ---------- EXIT ----------
    return random.choice([
        "OTP abhi nahi aaya, network issue hai",
        "thoda time do, phone hang ho raha hai",
        "main 2 minute mein karta hoon"
    ])
