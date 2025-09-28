from flask import Flask, jsonify
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

SUSPICIOUS_KEYWORDS = [
    "urgent", "verify", "account", "login", "password", "click", "confirm",
    "update", "security", "alert", "billing", "suspended", "unusual activity"
]

legit_domains = [
        "google.com", "gmail.com", "microsoft.com", "outlook.com",
        "hotmail.com", "apple.com", "icloud.com", "amazon.com",
        "facebook.com", "instagram.com", "twitter.com", "paypal.com",
        "stripe.com", "visa.com", "mastercard.com", "bankofamerica.com",
        "chase.com", "wellsfargo.com", "hsbc.com", "citibank.com",
        "dbs.com", "ocbc.com", "uob.com.sg", "ebay.com",
        "zoom.us", "linkedin.com", "netflix.com", "spotify.com",
        "youtube.com"
    ]


class Email:
    def __init__(self, sender, subject, body):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.riskScore = 0
        self.is_whitelisted = None

    def WhiteList_Check(self):
        # put logic remove pass
        df = pd.read_csv(WHITELIST)   # read whitelist csv
        if self.sender.strip().lower() in df['sender'].str.strip().str.lower().values:  # check if sender is in whitelist (case insensitive, removes trailing spaces)
            print(f"Sender in whitelist: {self.sender}")
            self.is_whitelisted = True      #output can be found in /emails route
            return self.is_whitelisted
        else:
            self.riskScore += 1 # increase risk score if not in whitelist
            print(f"Sender not in whitelist: {self.sender}")
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
        self.sender = domain

        for legit in legit_domains:
            distance = lev.distance(domain,legit)
            if distance == 0: 
                self.riskScore += 1
                print(f"[SAFE] Exact domain match: {domain} == {legit}. Risk +1")
                return f"[SAFE] This email {domain} is an exact match with {legit}"
            elif 1 <= distance <= 3:
                self.riskScore += 10
                print(f"[SUSPICIOUS] {domain} is similar to {legit}. Risk +10")
                return f"[SUSPICIOUS] {domain} looks similar to {legit}"
            
        print(f"[UNKNOWN] {domain} is not similar to any known domain")
        return f"[UNKNOWN] {domain} is not similar to any known domain"
    
    


    def  Keyword_Detection(self):
        # put logic remove pass
        found_keywords = []

        # Check subject
        subject_lower = self.subject.lower() if self.subject else ""
        for keyword in SUSPICIOUS_KEYWORDS:
            idx = subject_lower.find(keyword)
            if idx != -1:
                found_keywords.append((keyword, "subject", idx))
            
            # Check body
        body_lower = self.body.lower() if self.body else ""
        for keyword in SUSPICIOUS_KEYWORDS:
            idx = body_lower.find(keyword)
            if idx != -1:
                found_keywords.append((keyword, "body", idx))
        print("Found Keywords: ", found_keywords)
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
            #extract url from body
            match = re.search(r"(?P<url>https?://[^\s]+)", self.body)
            if match:
                print("URL found: ", match.group("url"))
                for email in match.group("url"):
                    # checks for typical url shorteners and file extensions
                    if "bit.ly" in email or "tinyurl.com" in email or "ow.ly" in email:
                        self.riskScore += 1
                    # checks for file extensions in url
                    elif ".exe" in email or ".zip" in email or ".rar" in email:
                        self.riskScore += 1
                    #check whether url is using secure http
                    elif "http://" in email:
                        self.riskScore += 1
            else:
                print("No URL found")
    
    def to_dict(self):
        return {
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "riskScore": self.riskScore,
            "is_whitelisted": self.is_whitelisted
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

