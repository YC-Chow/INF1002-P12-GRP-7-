import re

SUSPICIOUS_KEYWORDS = [
    "urgent", "verify", "account", "login", "password", "click",
    "confirm", "update", "security", "alert", "billing",
    "suspended", "unusual activity"
]

def clean_text(text):
    # Replace multiple whitespace (space, tab, newline) with a single space
    return re.sub(r"\s+", " ", text).strip()
