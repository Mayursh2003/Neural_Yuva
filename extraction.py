# extraction.py
import re

UPI_REGEX = re.compile(r"\b[\w.-]+@[\w.-]+\b")
PHONE_REGEX = re.compile(r"\b(?:\+91|91)?[6-9]\d{9}\b")
URL_REGEX = re.compile(r"https?://\S+")

SUSPICIOUS_KEYWORDS = [
    "urgent",
    "immediately",
    "verify",
    "account blocked",
    "suspended",
    "upi",
    "refund",
    "kyc"
]

def extract_intelligence(session: dict, text: str):
    t = text.lower()
    intel = session["extractedIntelligence"]

    for upi in UPI_REGEX.findall(text):
        if upi not in intel["upiIds"]:
            intel["upiIds"].append(upi)

    for phone in PHONE_REGEX.findall(text):
        if phone not in intel["phoneNumbers"]:
            intel["phoneNumbers"].append(phone)

    for url in URL_REGEX.findall(text):
        if url not in intel["phishingLinks"]:
            intel["phishingLinks"].append(url)

    for kw in SUSPICIOUS_KEYWORDS:
        if kw in t and kw not in intel["suspiciousKeywords"]:
            intel["suspiciousKeywords"].append(kw)

