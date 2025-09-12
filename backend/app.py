from flask import Flask, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)  # allow React to call Flask

@app.route("/api/hello")
def hello():
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
        # put logic remove pass
        pass

    def Final_Risk_Score(self):
        # put logic remove pass
        pass

if __name__ == "__main__":
    app.run(port=5000, debug=True)



