from flask import Flask, jsonify , request
from flask_cors import CORS
import re
import pandas as pd
import random
import Levenshtein as lev
import re


app = Flask(__name__)
CORS(app)  # allow React to call Flask
DATASET = "backend\\CEAS_08.csv"
WHITELIST = "backend\\whitelist.csv"

@app.route("/")
def hello():
    return jsonify(message="Hello from Flask backend!")

@app.route("/emails" , methods=["GET"])
def get_emails():
    # extracts x random emails on route load
    emailList = DatasetExtraction(10)
    for email in emailList:
        email.WhiteList_Check()
    Final_Risk_check(emailList)
    # convert list of Email objects to list of dicts
    email_dicts = [email.to_dict() for email in emailList]
    print(email_dicts)
    return jsonify(email_dicts)

@app.route("/distance")
# route for edit distance check testing
def distance():
    emailList = DatasetExtraction(5)
    for email in emailList:
        email.Edit_Distance_Check()
    email_dicts = [email.to_dict() for email in emailList]
    return jsonify(email_dicts)

@app.route("/url", methods=["GET"])
def url():
    emailList = DatasetExtraction(5)
    emailList.append(Email("", "Test Subject", "Please click http://192.168.0.1 to verify bit.ly/abc.zip"))
    for email in emailList:
        email.Sus_Url_Detection()
    email_dicts = [email.to_dict() for email in emailList]
    return jsonify(email_dicts)

@app.route("/analyze", methods=["POST"])
# route to analyze the email input from React web
def analyze_email():
    data = request.get_json()
    sender = data.get("sender", "")
    subject = data.get("subject", "")
    body = data.get("body", "")

    email = Email(sender, subject, body)
    email.WhiteList_Check()
    email.Edit_Distance_Check()
    email.Keyword_Position_Scoring()
    email.Sus_Url_Detection()

    return jsonify(email.to_dict())

SUSPICIOUS_KEYWORDS = [
    "urgent", "verify", "account", "login", "password", "click", "confirm",
    "update", "security", "alert", "billing", "suspended", "unusual activity"
]

legit_domains = [
        "google.com", "gmail.com", "yahoo.com" ,"microsoft.com", "outlook.com",
        "hotmail.com", "apple.com", "icloud.com", "amazon.com",
        "facebook.com", "instagram.com", "twitter.com", "paypal.com",
        "stripe.com","hotmail.com" ,"mastercard.com", "bankofamerica.com",
        "wellsfargo.com", "hsbc.com", "citibank.com",
        "ocbc.com", "uob.com.sg", "ebay.com",
        "zoom.us", "linkedin.com", "netflix.com", "spotify.com",
        "youtube.com"
    ]

def clean_text(text):
    # Replace multiple whitespace (space, tab, newline) with a single space
    return re.sub(r"\s+", " ", text).strip()


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
        df = pd.read_csv(WHITELIST)   # reads whitelist csv into pandas dataframe for efficient lookups
        if self.sender.strip().lower() in df['sender'].str.strip().str.lower().values:  # compare self.sender with whitelist (convert to lowercase, removes trailing spaces)
            self.is_whitelisted = True      #output can be found in /emails route
            return self.is_whitelisted
        else:
            self.riskScore = 10 # max risk score as sender not in whitelist
            self.is_whitelisted = False     #output can be found in /emails route
            return self.is_whitelisted

    def Edit_Distance_Check(self):
        
        def extract_domain(sender):
            # looks for a pattern inside <> using regex
            match = re.search(r'<([^<>]+@[^<>]+)>', sender)
            if match:
                # extract the email if its inside the <>
                email = match.group(1)
            else:
                email = sender
            #split the @ and get the domain
            domain = email.split('@')[-1].strip().lower()
            return domain

        domain = extract_domain(self.sender)

         # Quick exact match or subdomain check -> SAFE
        for legit in legit_domains:
            real = legit.strip().lower()
            distance = lev.distance(domain, real)

            # Exact or subdomain match
            if domain == real or domain.endswith("." + real):
                print(f"[SAFE] Exact/subdomain match: {domain} == {real}")
                return f"[SAFE] {domain} is an exact/subdomain match with {real}"

            # Suspicious (distance 1–3)
            elif 1 <= distance <= 3:
                self.riskScore = 10
                self.edit_distance_flag = True
                print(f"[SUSPICIOUS] {domain} is similar to {real} (distance={distance}). Risk set to 10")
                return f"[SUSPICIOUS] {domain} looks similar to {real}"

        # If no matches at all
        print(f"[UNKNOWN] {domain} is not similar to any known domain")
        return f"[UNKNOWN] {domain} is not similar to any known domain"


    def  Keyword_Detection(self):
        # Initializes an empty list to store matched keywords along with their location and position.
        found_keywords = []

        # Clean subject and body first
        subject_lower = clean_text(self.subject.lower()) if self.subject else ""
        body_lower = clean_text(self.body.lower()) if self.body else ""

        for keyword in SUSPICIOUS_KEYWORDS:
            # Regex pattern ensures keyword appears as a separate word
            #\b means a word boundary (space, punctuation, or start/end of string).
            # re.escape() ensures any special characters in the keyword are treated literally.
            # Example: keyword "click" → pattern \bclick\b. Matches "click.", " click " but not "clicking".
            pattern = r"\b" + re.escape(keyword) + r"\b"

            # Subject search
            for match in re.finditer(pattern, subject_lower):
                # If a match is found, append the keyword, its location, and position to the list.
                #re.finditer() finds all matches, not just the first one — so multiple occurrences per email are detected.
                found_keywords.append((keyword, "subject", match.start()))

            # Body search
            for match in re.finditer(pattern, body_lower):
                found_keywords.append((keyword, "body", match.start()))
        print("Found Keywords: ", found_keywords)
        self.detected_keywords = found_keywords
        return found_keywords
    
    def Keyword_Position_Scoring(self):
        """
        Assigns risk score based on keyword positions.
        - +3 if keyword in subject
        - +2 if keyword in first 100 chars of body
        - +1 if keyword elsewhere in body
        """
        found_keywords = self.Keyword_Detection()
        for keyword, location, position in found_keywords:
            if location == "subject":
                self.riskScore += 3
            elif location == "body":
                if position < 100:
                    self.riskScore += 2
                else:
                    self.riskScore += 1
        print("Current Risk Score: ", self.riskScore)
        return self.riskScore
        

    def Sus_Url_Detection(self):
        if self.body == None or self.body == "":
            print("No body")
            self.riskScore += 1
        else:
            # check for url shorteners
            if "bit.ly" in self.body or "tinyurl.com" in self.body or "ow.ly" in self.body:
                    print("URL Shortener found!")
                    self.riskScore += 1
            #extract url from body
            match = re.search(r"(?P<url>https?://[^\s]+)", self.body)
            if match:
                # regex to match ip address
                ipRegx = r'(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)' \
                            r'(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}'
                urlString = match.group("url")
                print("URL found: ", urlString)

                # check for .exe, .zip, .rar, http, ip address in url
                if ".exe" in urlString or ".zip" in urlString or ".rar" in urlString:
                    print("Executable found!")
                    self.riskScore += 1
                if "http://" in urlString:
                    print("HTTP found!")
                    self.riskScore += 1
                if re.search(ipRegx, urlString):
                    print("IP Add found!")
                    self.riskScore += 1
                
            else:
                print("No URL found")
    
    def to_dict(self):
        # this is to show the breakdown on the FRONTEND side (inside risk_breakdown)
        keyword_score = 0
        for kw, location, pos in self.detected_keywords:
            if location == "subject":
                keyword_score += 3
            elif location == "body":
                keyword_score += 2 if pos < 100 else 1

        return {
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "riskScore": self.riskScore,
            "is_whitelisted": self.is_whitelisted,
            "keywords": list(set([kw[0] for kw in self.detected_keywords])),
            "risk_breakdown": { # Breaksdown the overall riskscore into sub-components. Make it easy to show the frontend exactly the email has that riskscore
                "Whitelist": 10 if (self.is_whitelisted is False and not self.edit_distance_flag) else 0,
                "Edit Distance": 10 if self.edit_distance_flag else 0,
                "Keyword": keyword_score,
                "URL": 1 if "http://" in (self.body or "") else 0,
        }
    }
                
def Final_Risk_check(email_list):
    for email in email_list:
        email.WhiteList_Check()
        email.Edit_Distance_Check()
        if email.riskScore >= 10:
            #skips further checks as risk score is already max if any of the above checks fail
            continue  
        email.Keyword_Detection()
        email.Keyword_Position_Scoring()
        email.Sus_Url_Detection()

        email.riskScore = min(email.riskScore, 10)

def DatasetExtraction(count):
    df = pd.read_csv(DATASET)
    # There are 71487 rows in the dataset
    # extracting x number of random rows from the dataset
    random_numbers = [random.randint(1, 10000) for _ in range(count)]
    emailList = []

    i = 0
    while i < len(random_numbers):
        row = df.iloc[random_numbers[i]]
        if re.match(r"[^@]+@[^@]+\.[^@]+", row['sender']):
            # create Email object and append to list if valid email
            emailList.append(Email(row['sender'], row['subject'], row['body']))
        else:
        #if its not valid email, extract another random row
            random_numbers.append(random.randint(max(random_numbers), 10000))
        i += 1
        
    return emailList

if __name__ == "__main__":
    app.run(port=5000, debug=True)

