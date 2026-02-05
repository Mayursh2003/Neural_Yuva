

# extraction.py
import re

UPI_REGEX = r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}"
PHONE_REGEX = r"(?:\+91[-\s]?)?[6-9]\d{9}"
BANK_REGEX = r"\b\d{9,18}\b"

KEYWORDS = [
    "urgent", "verify", "otp", "blocked", "suspend",
    "upi", "account", "fraud", "immediately", "refund", "kyc", "lottery", "prize", "reward", "congratulations",
    "lucky draw", "case filed", "legal action", "arrest", "penalty", "complaint registered"
]


def extract_intelligence(session: dict, text: str):
    lower = text.lower()

    upis = re.findall(UPI_REGEX, text)
    phones = re.findall(PHONE_REGEX, text)
    banks = re.findall(BANK_REGEX, text)

    for u in upis:
        if u not in session["extractedIntelligence"]["upiIds"]:
            session["extractedIntelligence"]["upiIds"].append(u)

    for p in phones:
        if p not in session["extractedIntelligence"]["phoneNumbers"]:
            session["extractedIntelligence"]["phoneNumbers"].append(p)

    for b in banks:
        if b not in session["extractedIntelligence"]["bankAccounts"]:
            session["extractedIntelligence"]["bankAccounts"].append(b)

    for k in KEYWORDS:
        if k in lower and k not in session["extractedIntelligence"]["suspiciousKeywords"]:
            session["extractedIntelligence"]["suspiciousKeywords"].append(k)
