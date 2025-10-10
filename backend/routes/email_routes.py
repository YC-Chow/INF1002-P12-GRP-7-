from flask import Blueprint, jsonify, request
from models.email_model import Email
from utils.dataset_utils import DatasetExtraction, Final_Risk_check

email_bp = Blueprint("email_bp", __name__)

@email_bp.route("/")
def hello():
    return jsonify(message="Hello from Flask backend!")

@email_bp.route("/emails", methods=["GET"])
def get_emails():
    emailList = DatasetExtraction(10)
    for email in emailList:
        email.WhiteList_Check()
    Final_Risk_check(emailList)
    return jsonify([email.to_dict() for email in emailList])

@email_bp.route("/distance")
def distance():
    emailList = DatasetExtraction(5)
    for email in emailList:
        email.Edit_Distance_Check()
    return jsonify([email.to_dict() for email in emailList])

@email_bp.route("/url")
def url():
    emailList = DatasetExtraction(5)
    emailList.append(Email("", "Test Subject", "Please click http://192.168.0.1 to verify bit.ly/abc.zip"))
    for email in emailList:
        email.Sus_Url_Detection()
    return jsonify([email.to_dict() for email in emailList])

@email_bp.route("/analyze", methods=["POST"])
def analyze_email():
    data = request.get_json()
    email = Email(data.get("sender", ""), data.get("subject", ""), data.get("body", ""))
    email.WhiteList_Check()
    email.Edit_Distance_Check()
    email.Keyword_Position_Scoring()
    email.Sus_Url_Detection()
    return jsonify(email.to_dict())
