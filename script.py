
from dotenv import load_dotenv
from peewee import *
from datetime import datetime
import requests
import os
import smtplib
import json
import ssl
import sys

from src.app import *
from src.auth import *

from dotenv import load_dotenv

load_dotenv()


truelayer_client_id = os.getenv("truelayer_client_id")
truelayer_client_secret = os.getenv("truelayer_client_secret")
monzo_client_id = os.getenv("monzo_client_id")
monzo_client_secret = os.getenv("monzo_client_secret")


def sendmail(subject, body):
    try:
        message = f"""
        Subject:{subject}

        {body}"""

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT"), context=context) as server:
            server.login(os.getenv("SMTP_USERNAME"),
                         os.getenv("SMTP_PASSWORD"))
            server.sendmail(os.getenv("SMTP_SENDER_EMAIL"),
                            os.getenv("EMAIL"), message)
    except:
        pass


def get_refresh_token():
    url = "https://auth.truelayer.com/connect/token"

    payload = {
        "grant_type": "refresh_token",
        "client_id": truelayer_client_id,
        "client_secret": truelayer_client_secret,
        "redirect_uri": "https://console.truelayer.com/redirect-page",
        "refresh_token": Data.get(Data.key == "truelayer_refresh_token").value,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if not response.ok:
        return False
    Data.update(value=response.json()["access_token"]).where(
        Data.key == "truelayer_access_token").execute()
    Data.update(value=response.json()["refresh_token"]).where(
        Data.key == "truelayer_refresh_token").execute()
    return True


def get_transactions():
    if not Data.get_or_none(key="truelayer_access_token"):
        print("No access token has been found. Please run authentication script.")
        exit()
    access_token = Data.get_or_none(key="truelayer_access_token").value
    account_id = Data.get(key="truelayer_account_id").value
    auth_header = {'Authorization': f'Bearer {access_token}'}
    #Below is getting the Pending transactions and adding them to database
    res = requests.get(
        f'https://api.truelayer.com/data/v1/cards/{account_id}/transactions/pending', headers=auth_header)
    if not res.ok:
        return False

    transactions = res.json()['results']
    for transaction in transactions:
        Transactions.get_or_create(
            amount=transaction["amount"],
            description=transaction["description"],
            timestamp=transaction["timestamp"])
    #Below is getting the completed transactions and added them to database
    res = requests.get(
        f'https://api.truelayer.com/data/v1/cards/{account_id}/transactions', headers=auth_header)
    if not res.ok:
        return False

    transactions = res.json()['results']
    for transaction in transactions:
        Transactions.get_or_create(
            amount=transaction["amount"],
            description=transaction["description"],
            timestamp=transaction["timestamp"])
    return True


def monzo_refresh_token():

    url = "https://api.monzo.com/oauth2/token"

    payload = {
        "grant_type": "refresh_token",
        "client_id": monzo_client_id,
        "client_secret": monzo_client_secret,
        "refresh_token": Data.get(Data.key == "monzo_refresh_token").value,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    

    if not response.ok:
        return False
    Data.update(value=response.json()["access_token"]).where(
        Data.key == "monzo_access_token").execute()
    Data.update(value=response.json()["refresh_token"]).where(
        Data.key == "monzo_refresh_token").execute()
    return True


def monzo_them():

    for transaction in Transactions.select().where(Transactions.monzoed == None or Transactions.monzoed != 1):
        amount = int(transaction.amount*100)
        if monzo(amount):
            Transactions.update(monzoed=1).where(
                Transactions.id == transaction.id).execute()
            return True
        else:
            print("Could not monzo them :(")
            print("Trying to reauth with Monzo!")
            return False
    return True


def monzo(amount):

    amount = int(amount)
    pot = os.getenv("pot_id")
    url = f"https://api.monzo.com/pots/{pot}/deposit"
    access_token = Data.get(key="monzo_access_token").value

    payload = {
        "source_account_id": os.getenv("monzo_account_id"),
        "amount": amount,
        "dedupe_id": datetime.now()
    }

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.put(url, data=payload, headers=headers)

    if not response.ok:
        message = json.loads(response.text)
        if message["code"] == "bad_request.insufficient_funds":
            print("Error! Your Monzo account has insufficient funds!")
            exit()
        elif message["code"] == "forbidden.insufficient_permissions":
            print("Error! Please allow permission in the Monzo app!")
            exit()
        print("error monzoing! error is:")
        print(response.text)

        return False

    return True


def warn(service):
    print(
        f"Error! Despite attempting to refresh its token, {service.capitalize()}, still cannot be reached. Please try running auth.py!")
    #sendmail(f"Error on {service}",
             #f"Error! Despite attempting to refresh its token {service.capitalize()} still cannot be reached. Please check application!")

try:
    command = sys.argv[1]
except:
    print(f"Invalid Usage: python {sys.argv[0]} run|auth")
    exit()

if command == "run":
    if not get_transactions():
        print("Refreshing Truelayer token!")
        get_refresh_token()
        if not get_transactions():
           warn("truelayer")
        else:
            if not monzo_them():
                monzo_refresh_token()
                if not monzo_them():
                    warn("monzo")
                    exit()
    else:
        if not monzo_them():
            monzo_refresh_token()
            if not monzo_them():
                warn("monzo")
                exit()

elif command == "auth":
    print("Welcome to the amex-monzo authenticaton script!")
    arg = input("Is this your first time? (yes/no): ")
    if arg == "yes":
        auth()
    elif arg == "no":
        reauth()
    else:
        print("Invalid Input")
else:
    print(f"Invalid Usage: python {sys.argv[0]} run|auth")
    exit()