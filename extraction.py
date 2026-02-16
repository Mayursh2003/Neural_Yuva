# extraction.py
import re


# ---------------- REGEX (INDIA-SPECIFIC, FORGIVING) ----------------

UPI_REGEX = re.compile(
    r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b"
)

PHONE_REGEX = re.compile(
    r"(?:\+91[-\s]?)?[6-9]\d{9}"
)

# catches 9–18 digit numbers but avoids OTPs like 4–6 digits
BANK_REGEX = re.compile(
    r"\b\d{9,18}\b"
)

LINK_REGEX = re.compile(
    r"(https?:\/\/[^\s]+)"
)

KEYWORDS = [
    "urgent", "immediately", "verify", "otp",
    "blocked", "suspend", "freeze",
    "upi", "account", "fraud",
    "security team", "customer care",
    "last chance", "time left"
]


# ---------------- CORE EXTRACTION ----------------

def extract_intelligence(session: dict, text: str):
    """
    Extracts scam intelligence incrementally.
    Never deletes existing data.
    Never blocks conversation.
    """

    if not text:
        return

    lower = text.lower()
    intel = session["extractedIntelligence"]

    # ---- UPI IDs ----
    for upi in UPI_REGEX.findall(text):
        if upi not in intel["upiIds"]:
            intel["upiIds"].append(upi)

    # ---- Phone Numbers ----
    for phone in PHONE_REGEX.findall(text):
        cleaned = phone.replace(" ", "").replace("-", "")
        if cleaned not in intel["phoneNumbers"]:
            intel["phoneNumbers"].append(cleaned)

    # ---- Bank / Account Numbers ----
    for num in BANK_REGEX.findall(text):
        # avoid OTP-like numbers
        if 9 <= len(num) <= 18:
            if num not in intel["bankAccounts"]:
                intel["bankAccounts"].append(num)

    # ---- Phishing Links ----
    for link in LINK_REGEX.findall(text):
        if link not in intel["phishingLinks"]:
            intel["phishingLinks"].append(link)

    # ---- Suspicious Keywords ----
    for kw in KEYWORDS:
        if kw in lower and kw not in intel["suspiciousKeywords"]:
            intel["suspiciousKeywords"].append(kw)