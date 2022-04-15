from app import Data, Transactions
from dotenv import load_dotenv
from peewee import *
import requests
import os

from dotenv import load_dotenv

load_dotenv()


truelayer_client_id = os.getenv("truelayer_client_id")
truelayer_client_secret = os.getenv("truelayer_client_secret")
monzo_client_id = os.getenv("monzo_client_id")
monzo_client_secret = os.getenv("monzo_client_secret")

def get_refresh_token():
    url = "https://auth.truelayer.com/connect/token"


    payload = {
        "grant_type": "refresh_token",
        "client_id": truelayer_client_id,
        "client_secret": truelayer_client_secret,
        "redirect_uri": "https://console.truelayer.com/redirect-page",
        "refresh_token": Data.get(Data.key == "refresh_token").value,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    

    if not response.ok:
        return False
        print(response)
    Data.update(value = response.json()["access_token"]).where(Data.key == "access_token").execute()
    Data.update(value = response.json()["refresh_token"]).where(Data.key == "refresh_token").execute()
    return True

def get_transactions():
    access_token = Data.get(key="access_token").value
    account_id = Data.get(key="account_id").value
    auth_header = {'Authorization': f'Bearer {access_token}'}
    res = requests.get(
        f'https://api.truelayer.com/data/v1/cards/{account_id}/transactions/pending', headers=auth_header)
    if not res.ok:
        return False

    transactions = res.json()['results']
    for transaction in transactions:
        Transactions.get_or_create(
            transaction_id=transaction["transaction_id"],
            amount=transaction["amount"],
            description=transaction["description"])
    return True

def monzo_refresh_token():


    url = "https://api.monzo.com/oauth2/token"


    payload = {
        "grant_type": "refresh_token",
        "client_id": monzo_client_id,
        "client_secret": monzo_client_secret,
        "refresh_token": Data.get(Data.key == "refresh_token").value,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    

    if not response.ok:
        return False
    Data.update(value = response.json()["access_token"]).where(Data.key == "monzo_access_token").execute()
    Data.update(value = response.json()["refresh_token"]).where(Data.key == "monzo_refresh_token").execute()
    return True

def monzo_them():

    #Get ready to monzo them!
    for transaction in Transactions.select().where(Transactions.monzoed == None or Transactions.monzoed != 1):
        amount = int(transaction.amount*100)
        if monzo(amount):
            Transactions.update(monzoed = 1).where(Transactions.id == transaction.id).execute()
        else:
            print("Could not monzo them :(")
            print("Trying reauthenticating Monzo!")

def monzo(amount):

    amount = int(amount)
    pot = os.getenv("pot_id")
    url = f"https://api.monzo.com/pots/{pot}/deposit"
    access_token = Data.get(key = "monzo_access_token").value

    payload = {
        "source_account_id": os.getenv("monzo_account_id"),
        "amount": amount,
        "dedupe_id": amount*2,
    }

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.put(url, data=payload, headers=headers)
    
    if not response.ok:
        print("error monzoing! error is:")
        print(response.text)
        return False

    return True


if not get_transactions():
    print("Refreshing Truelayer token!")
    get_refresh_token()
    if not get_transactions():
        print("ERROR! Truelayer needs to be re-authenticated. Please run auth.py")
    else:
        monzo_them()
else:
    monzo_them()
        