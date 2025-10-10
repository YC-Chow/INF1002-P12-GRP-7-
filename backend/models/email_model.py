import re
import pandas as pd
import Levenshtein as lev
from utils.text_utils import clean_text, SUSPICIOUS_KEYWORDS, SHORTENERS, EXTENSIONS
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
        self.urlRisk = 0


    def WhiteList_Check(self):
        df = pd.read_csv(WHITELIST)  #loads the whitelist csv into a dataframe
        
        def extract_domain(sender):     #extracts domain from email address
            match = re.search(r'<([^<>]+)>', sender)  #looks for pattern inside <>, easier than manually editing all the data in the csv
            #example of email format in dataset: Young Esposito <Young@iworld.de>

            email = match.group(1) if match else sender  #if match, it will retrieve what is inside <>, else it returns None and keep the original string
            return email.split('@')[-1].strip().lower()  #extract and return the domain part of the email address 
            #does this by splitting the email string at '@' and taking the last part, which is the domain
        
        sender_domain = extract_domain(self.sender) #extract domain from sender
        sender_domain = sender_domain.lower()   #lowercase for case insensitive comparison
        df['domain'] = df['sender'].apply(extract_domain).str.lower()  
        #creates new column in whitelist dataframe labelled 'domain' by applying domain extraction to sender column in whitelist, 
        #lowercase for case insensitive comparison

        if sender_domain in df['domain'].values:        #check if the extracted sender domain is in the domain column of the whitelist
            self.is_whitelisted = True     #indicate as whitelisted
            print(f"Sender's domain {sender_domain} is whitelisted.")   #for checking purposes
        else:
            self.is_whitelisted = False  #indicate as not whitelisted
            self.riskScore = 10  #assign max risk score since not whitelisted
            print(f"Sender's domain {sender_domain} is NOT whitelisted.")   #for checking purposes
            
        return self.is_whitelisted


    def Edit_Distance_Check(self):
        def extract_domain(sender):
            # looks for a pattern inside the <> regex
            match = re.search(r'<([^<>]+@[^<>]+)>', sender)
            # if match, it will retrieve what is inside <>, else it returns None and keep the original string
            email = match.group(1) if match else sender
            # split the @ and get the domain
            return email.split('@')[-1].strip().lower()

        # extract the sender domain
        domain = extract_domain(self.sender)

        for legit in legit_domains:
            real = legit.strip().lower()
            # calculate how many characters edits are needed to change "domain" to "real"
            distance = lev.distance(domain, real)
            # converts the distance into ratio to account the domain length differences
            similarity_ratio = distance / max(len(domain), len(real))
            
            # Exact or subdomain match
            if domain == real or domain.endswith("." + real):
                print(f"[SAFE] Exact domain match : {domain} == {real}")
                return f"[SAFE] {domain} == {real}"
            
            # Suspicious (distance 0-1)
            # domains that are <=20% different are considered suspicious 
            elif 0 <= similarity_ratio <= 0.2:
                self.riskScore = 10
                # this flag is for the frontend part
                self.edit_distance_flag = True
                print(f"[SUSPICIOUS] {domain} is similar to {real} (distance = {distance}). Risk set to 10" )
                return f"[SUSPICIOUS] {domain} looks similar to {real}"

        print(f"[UNKNOWN] {domain} not similar to known domains")
        return f"[UNKNOWN] {domain} not similar to known domains"

    def Keyword_Detection(self):
        # Initialize an empty list to store found keywords with their locations and positions
        found_keywords = []

        # Clean subject and body first
        # Replace multiple whitespace (space, tab, newline) with a single space
        #clean_text() function imported from text_utils.py
        subject_lower = clean_text(self.subject.lower()) if self.subject else ""
        body_lower = clean_text(self.body.lower()) if self.body else ""

        for keyword in SUSPICIOUS_KEYWORDS:
            # Use regex for full word matching
            # Regex pattern ensures keyword appears as a separate word
            # \b means a word boundary (space, punctuation, or start/end of string)
            # re.escape() ensures any special characters in keyword are treated literally
            # Example: "click" → keyword: click works. But "cli\nck" won't match.
            pattern = r"\b" + re.escape(keyword) + r"\b"

            # Subject search
            for match in re.finditer(pattern, subject_lower):
                found_keywords.append((keyword, "subject", match.start()))

            # Body search
            for match in re.finditer(pattern, body_lower):
                found_keywords.append((keyword, "body", match.start()))

        self.detected_keywords = found_keywords
        return found_keywords

    def Keyword_Position_Scoring(self):
        """ 
        Assigns risk score based on keyword positions. 
        - +3 if keyword in subject 
        - +2 if keyword in first 100 chars of body 
        - +1 if keyword elsewhere in body 
        """
        # Call the Keyword_Detection() method to get all detected keywords.
        # It returns a list of tuples in the form (keyword, location, position),
        # where 'location' can be "subject" or "body", and 'position' is the index of the keyword.
        found_keywords = self.Keyword_Detection()

        #Loop through the found keywords and adjust riskScore based on their location and position.
        for keyword, location, pos in found_keywords:
            if location == "subject":
                self.riskScore += 3
            elif location == "body":
                self.riskScore += 2 if pos < 100 else 1
        #print("Current Risk Score: ", self.riskScore)
        return self.riskScore

    def Sus_Url_Detection(self):
        if self.body == None or self.body == "":
            #skips URL checks if body is empty
            return

        # Check for known URL shorteners
        if any(x in self.body for x in SHORTENERS):
            self.riskScore += 1
    
        # Regex to find all URLs
        urls = re.findall(r"(?P<url>https?://[^\s]+)", self.body)
        ip_regex = r'(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}'
        if not urls:
            print("No URLs found.")
            #skip URL checks if no URLs present
            return
        
        for url in urls:
            # check for extensons in url
            if any(ext in url for ext in EXTENSIONS):
                self.riskScore += 1
                self.urlRisk += 1
            # check whether using https or not
            if "http://" in url:
                self.riskScore += 1
                self.urlRisk += 1
            # check for IP address in URL
            if re.search(ip_regex, url):
                self.riskScore += 1
                self.urlRisk += 1
       

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
                "URL": self.urlRisk,
            },
        }
