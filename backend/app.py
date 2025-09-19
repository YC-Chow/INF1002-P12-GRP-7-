from flask import Flask, jsonify
from flask_cors import CORS
import re
import pandas as pd
import random

app = Flask(__name__)
CORS(app)  # allow React to call Flask
DATASET = "backend\\CEAS_08.csv"

@app.route("/")
def hello():
    emailList = DatasetExtraction(5)
    for email in emailList:
        print(email.sender)
    return jsonify(message="Hello from Flask backend!")

@app.route("/emails")
def get_emails():
    emailList = DatasetExtraction(10)
    Final_Risk_check(emailList)
    email_dicts = [email.to_dict() for email in emailList]
    print(email_dicts)
    return jsonify(email_dicts)


class Email:
    def __init__(self, sender, subject, body):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.riskScore = 0

    def Edit_Distance_Check(self):
        # put logic remove pass
        pass

    def WhiteList_Check(self):
        # put logic remove pass
        pass

    def  Keyword_Detection(self):
        # put logic remove pass
        pass

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
            "riskScore": self.riskScore
        }
                
def Final_Risk_check(email_list):
    for email in email_list:
        email.Edit_Distance_Check()
        email.WhiteList_Check()
        email.Keyword_Detection()
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
            emailList.append(Email(row['sender'], row['subject'], row['body']))
        else:
        #if its not valid email, extract another random row
            random_numbers.append(random.randint(max(random_numbers), 10000))
        i += 1
        
    return emailList

if __name__ == "__main__":
    app.run(port=5000, debug=True)



