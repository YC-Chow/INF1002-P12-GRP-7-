import re
import pandas as pd
import Levenshtein as lev
from utils.text_utils import clean_text, SUSPICIOUS_KEYWORDS
from config import WHITELIST, legit_domains


class Email:
    def __init__(self, sender, subject, body):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.riskScore = 0
        self.is_whitelisted = None
        self.detected_keywords = []
        self.edit_distance_flag = False

    def WhiteList_Check(self):
        df = pd.read_csv(WHITELIST)
        sender_clean = self.sender.strip().lower()
        if sender_clean in df['sender'].str.strip().str.lower().values:
            self.is_whitelisted = True
        else:
            self.is_whitelisted = False
            self.riskScore = 10
        return self.is_whitelisted

    def Edit_Distance_Check(self):
        def extract_domain(sender):
            match = re.search(r'<([^<>]+@[^<>]+)>', sender)
            email = match.group(1) if match else sender
            return email.split('@')[-1].strip().lower()

        domain = extract_domain(self.sender)

        for legit in legit_domains:
            real = legit.strip().lower()
            distance = lev.distance(domain, real)

            if domain == real or domain.endswith("." + real):
                return f"[SAFE] {domain} == {real}"
            elif 1 <= distance <= 3:
                self.riskScore = 10
                self.edit_distance_flag = True
                return f"[SUSPICIOUS] {domain} looks similar to {real}"

        return f"[UNKNOWN] {domain} not similar to known domains"

    def Keyword_Detection(self):
        found_keywords = []
        subject_lower = clean_text(self.subject.lower()) if self.subject else ""
        body_lower = clean_text(self.body.lower()) if self.body else ""

        for keyword in SUSPICIOUS_KEYWORDS:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            for match in re.finditer(pattern, subject_lower):
                found_keywords.append((keyword, "subject", match.start()))
            for match in re.finditer(pattern, body_lower):
                found_keywords.append((keyword, "body", match.start()))

        self.detected_keywords = found_keywords
        return found_keywords

    def Keyword_Position_Scoring(self):
        found_keywords = self.Keyword_Detection()
        for keyword, location, pos in found_keywords:
            if location == "subject":
                self.riskScore += 3
            elif location == "body":
                self.riskScore += 2 if pos < 100 else 1
        return self.riskScore

    def Sus_Url_Detection(self):
        if not self.body:
            self.riskScore += 5
            return

        # Check for known URL shorteners
        if any(x in self.body for x in ["bit.ly", "tinyurl.com", "ow.ly"]):
            self.riskScore += 1

        # Regex to find URLs
        match = re.search(r"(?P<url>https?://[^\s]+)", self.body)
        if match:
            url = match.group("url")
            ip_regex = r'(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}'
            
            # check for extensons in url
            if any(ext in url for ext in [".exe", ".zip", ".rar"]):
                self.riskScore += 1
            # check whether using https or not
            if "http://" in url:
                self.riskScore += 1
            # check for IP address in URL
            if re.search(ip_regex, url):
                self.riskScore += 1

    def to_dict(self):
        keyword_score = 0
        for kw, loc, pos in self.detected_keywords:
            keyword_score += 3 if loc == "subject" else (2 if pos < 100 else 1)

        return {
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "riskScore": self.riskScore,
            "is_whitelisted": self.is_whitelisted,
            "keywords": list(set([kw for kw, _, _ in self.detected_keywords])),
            "risk_breakdown": {
                "Whitelist": 10 if (self.is_whitelisted is False and not self.edit_distance_flag) else 0,
                "Edit Distance": 10 if self.edit_distance_flag else 0,
                "Keyword": keyword_score,
                "URL": 1 if "http://" in (self.body or "") else 0,
            },
        }
