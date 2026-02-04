# detection.py

SCAM_PATTERNS = {
    "BANK_KYC": {
        "keywords": [
            "account blocked", "account suspended", "kyc update",
            "verify your account", "bank will block",
            "limited access", "restricted"
        ],
        "weight": 3
    },

    "LOTTERY_SCAM": {
        "keywords": [
            "lottery", "won", "you win", "congratulations",
            "lucky draw", "prize", "reward"
        ],
        "weight": 2
    },

    "REFUND_SCAM": {
        "keywords": [
            "refund", "mistaken", "by mistake", "sent by mistake",
            "galti se", "galat transfer", "jama ho gaye",
            "amount credited", "return money"
        ],
        "weight": 3
    },

    "UPI_FRAUD": {
        "keywords": [
            "upi", "collect request", "approve payment",
            "gpay", "phonepe", "paytm", "scan and pay"
        ],
        "weight": 4
    },

    "IMPERSONATION": {
        "keywords": [
            "rbi", "bank officer", "customer care",
            "support team", "govt", "police"
        ],
        "weight": 4
    },

    "LINK_PHISHING": {
        "keywords": [
            "http", "https", ".apk", "download app",
            "click link", "verify link"
        ],
        "weight": 5
    },

    "THREAT_SCAM": {
        "keywords": [
            "legal action", "case filed", "arrest",
            "penalty", "complaint registered", "suspend"
        ],
        "weight": 5
    }
}

SCAM_ARCHETYPES = {
    "THREAT_SCAM": ["blocked", "kyc", "suspend", "legal", "arrest"],
    "LOTTERY_SCAM": ["won", "lottery", "prize", "reward"],
    "REFUND_SCAM": ["mistaken", "galti", "refund", "sent by mistake"],
    "AUTHORITY_SCAM": ["bank officer", "rbi", "police"],
    "JOB_SCAM": ["job", "hiring", "salary", "work from home"]
}

SCAM_THRESHOLD = 4


def classify_scam_type(text: str):
    t = text.lower()
    for archetype, kws in SCAM_ARCHETYPES.items():
        if any(k in t for k in kws):
            return archetype
    return "GENERIC_SCAM"


def detect_scam(text: str, session: dict):
    text_lower = text.lower()
    total_score = 0
    detected_types = []

    for scam_type, data in SCAM_PATTERNS.items():
        for kw in data["keywords"]:
            if kw in text_lower:
                total_score += data["weight"]
                detected_types.append(scam_type)
                break

    # confidence accumulation (human-like gradual suspicion)
    session["scamConfidence"] = min(
        1.0,
        session.get("scamConfidence", 0.0) + (total_score / 10)
    )

    if total_score >= SCAM_THRESHOLD:
        return True, classify_scam_type(text)

    return False, None
