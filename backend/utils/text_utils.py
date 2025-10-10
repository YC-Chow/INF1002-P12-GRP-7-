import re

SUSPICIOUS_KEYWORDS = [
    "urgent", "verify", "account", "login", "password", "click",
    "confirm", "update", "security", "alert", "billing",
    "suspended", "unusual activity"
]

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()
