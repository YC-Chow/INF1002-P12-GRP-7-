from flask import Flask, jsonify
from flask_cors import CORS
import re
import pandas as pd
import random

app = Flask(__name__)
CORS(app)  # allow React to call Flask
DATASET = "backend\\CEAS_08.csv"

@app.route("/api/hello")
def hello():
    emailList = DatasetExtraction(5)
    return jsonify(message="Hello from Flask backend!")



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
            else:
                print("No URL found")
        # put logic remove pass
        pass

    def Final_Risk_Score(self):
        # put logic remove pass
        pass

def DatasetExtraction(count):
    df = pd.read_csv(DATASET)
    random_numbers = [random.randint(0, 5000) for _ in range(count)]
    emailList = []

    for num in random_numbers:
        row = df.iloc[num]
        emailList.append(Email(row['sender'], row['subject'], row['body']))
    
    for email in emailList:
        print(email.sender)
    return emailList

if __name__ == "__main__":
    app.run(port=5000, debug=True)



