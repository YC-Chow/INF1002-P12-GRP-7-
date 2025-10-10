import pandas as pd
import random
import re
from models.email_model import Email
from config import DATASET

def DatasetExtraction(count):
    df = pd.read_csv(DATASET)
    random_numbers = [random.randint(1, 10000) for _ in range(count)]
    emailList = []

    i = 0
    while i < len(random_numbers):
        row = df.iloc[random_numbers[i]]
        if re.match(r"[^@]+@[^@]+\.[^@]+", row['sender']):
            emailList.append(Email(row['sender'], row['subject'], row['body']))
        else:
            random_numbers.append(random.randint(max(random_numbers), 10000))
        i += 1
    return emailList


def Final_Risk_check(email_list):
    for email in email_list:
        email.WhiteList_Check()
        email.Edit_Distance_Check()
        if email.riskScore >= 10:
            continue
        email.Keyword_Detection()
        email.Keyword_Position_Scoring()
        email.Sus_Url_Detection()
        email.riskScore = min(email.riskScore, 10)
