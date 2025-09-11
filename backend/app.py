from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow React to call Flask

@app.route("/api/hello")
def hello():
    return jsonify(message="Hello from Flask backend!")

if __name__ == "__main__":
    app.run(port=5000, debug=True)

class Email:
    def __init__(self, sender, subject, body, urlFlag):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.urlFlag = urlFlag

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
        # put logic remove pass
        pass

    def Final_Risk_Score(self):
        # put logic remove pass
        pass