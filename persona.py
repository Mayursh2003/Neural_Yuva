# persona.py
import random


def generate_reply(session: dict):
    """
    Human-style Indian victim persona.
    No emojis.
    No repetition.
    Moves conversation forward gently.
    """

    phase = session.get("engagementPhase", "HOOK")

    # -------- HOOK: Fear + compliance --------
    if phase == "HOOK":
        replies = [
            "achha, mujhe samajh nahi aa raha hai, aap batao kya karna hoga",
            "theek hai, bas account safe rehna chahiye",
            "main thoda ghabra gaya hoon, aap process bata do",
        ]
        return random.choice(replies)

    # -------- MILK: Make scammer explain --------
    if phase == "MILK":
        replies = [
            "aap ek baar poora process bata do, step by step",
            "pehle kya karna hota hai, phir kya hota hai?",
            "main galat na kar doon isliye pooch raha hoon",
            "aap jaise bol rahe ho, waise hi follow karna hai na?",
        ]
        return random.choice(replies)

    # -------- VERIFY: Soft clarification, not challenge --------
    if phase == "VERIFY":
        replies = [
            "jo aap bol rahe ho, woh SMS mein bhi aata hai kya?",
            "UPI request ka naam wahi dikhega jo aap bata rahe ho?",
            "account number poora dena hota hai ya last digits?",
            "OTP aane ke baad next step kya hota hai?",
        ]
        return random.choice(replies)

    # -------- EXIT: Delay without confrontation --------
    replies = [
        "OTP abhi aaya nahi hai, thoda wait karna padega",
        "network thoda slow hai, ek minute do",
        "main check karke batata hoon, thoda time lagega",
    ]
    return random.choice(replies)