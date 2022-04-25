
from dotenv import load_dotenv
import requests
import os
from src.app import *

load_dotenv()

truelayer_client_id = os.getenv("truelayer_client_id")
truelayer_client_secret = os.getenv("truelayer_client_secret")
monzo_client_id = os.getenv("monzo_client_id")
monzo_client_secret = os.getenv("monzo_client_secret")

def truelayer_auth_user():
    print('Please visit the following link and copy the token')
    print(f"https://auth.truelayer.com/?response_type=code&client_id={truelayer_client_id}&scope=info%20cards%20transactions%20offline_access%20balance&redirect_uri=https://console.truelayer.com/redirect-page&providers=uk-ob-barclaycard%20uk-ob-capital-one%20uk-ob-tesco%20uk-oauth-amex")
    code = input("Please enter the code: ")
    Data.delete().where(Data.key == "truelayer_auth_code").execute()
    Data.create(key="truelayer_auth_code", value=code)

def truelayer_get_access_token():
    url = "https://auth.truelayer.com/connect/token"

    payload = {
        "grant_type": "authorization_code",
        "client_id": truelayer_client_id,
        "client_secret": truelayer_client_secret,
        "redirect_uri": "https://console.truelayer.com/redirect-page",
        "code": Data.get(Data.key == "truelayer_auth_code").value,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if not response.ok:
        print("Could not get access_token! There must be a problem with the auth code!")
        exit()

    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    try:
        Data.delete().where(key="truelayer_access_token").execute()
        Data.delete().where(key="truelayer_refresh_token").execute()
    except:
        pass
    Data.create(key="truelayer_access_token", value=access_token)
    Data.create(key="truelayer_refresh_token", value=refresh_token)

def truelayer_get_account_id():
    access_token = Data.get(key="truelayer_access_token").value
    auth_header = {'Authorization': f'Bearer {access_token}'}
    res = requests.get(
        'https://api.truelayer.com/data/v1/cards', headers=auth_header)
    account_id = (res.json()['results'][0])['account_id']
    try:
        Data.delete().where(key="truelayer_account_id").execute()
    except:
        pass
    Data.create(key="truelayer_account_id", value=account_id)

def monzo_token():
    auth_token = Data.get(key="monzo_auth_token").value
    print(auth_token)
    url = "https://api.monzo.com/oauth2/token"

    payload = {
        "grant_type": "authorization_code",
        "client_id": monzo_client_id,
        "client_secret": monzo_client_secret,
        "redirect_uri": "http://127.0.0.1:5000/callback",
        "code": auth_token,
    }

    response = requests.request ("POST", url, data=payload)
    if not response.ok:
        print("Could not get access_token! There must be a problem with the auth code!")
        print("Let's try one more time!")
        get_new_monzo()

    access_token = response.json()["access_token"]
    try:
        Data.delete().where(Data.key=="monzo_access_token").execute()
    except:
        pass
    Data.create(key="monzo_access_token", value=access_token)
    try:
        refresh_token = response.json()["refresh_token"]
        Data.create(key="monzo_refresh_token", value=refresh_token)
    except:
        print("We failed to get a refresh token! This is not our fault and is a problem on Monzo's side. The script will work but only for the next 24 hours and we will not be able to automatically refresh. In other words, you will have to manually re-auth in about 24 hours.")
        pass

def get_new_monzo():
    print("Okay this one is a little less obvious.")
    print('Go to the following link, login, and copy the code from link you receive in the email.')
    print("The page should be blank, on the URL copy between 'code=' and the '&state' EXCLUDING THE '&'!")
    print(f"https://auth.monzo.com/?client_id={monzo_client_id}&redirect_uri=http://127.0.0.1:5000/callback&response_type=code&state=hellothere")
    code = input("Please enter the code: ")
    try:
        Data.delete().where(Data.key == "monzo_auth_token").execute()
    except:
        pass
    Data.create(key="monzo_auth_token", value=code)
    print("Thanks! Attempting to get a Monzo Access Token!")
    monzo_token()

def check_variables():
    if os.getenv("truelayer_client_id") is None:
        print("Could not find truelayer_client_id! See docs.")
        exit()
    if os.getenv("truelayer_client_secret") is None:
        print("Could not find truelayer_client_secret! See docs.")
        exit()
    if os.getenv("monzo_client_id") is None:
        print("Could not find monzo_client_id! See docs.")
        exit()
    if os.getenv("monzo_client_secret") is None:
        print("Could not find monzo_client_secret! See docs.")
        exit()
    if os.getenv("pot_id") is None:
        print("Could not find pot_id! See docs.")
        exit()
    if os.getenv("monzo_account_id") is None:
        print("Could not find pot_id! See docs.")
        exit()

def check_balance_for_testing_purposes():
    access_token = Data.get(key="truelayer_access_token").value
    account_id = Data.get(key="truelayer_account_id").value
    auth_header = {'Authorization': f'Bearer {access_token}'}
    res = requests.get(
        f'https://api.truelayer.com/data/v1/cards/{account_id}/balance', headers=auth_header)
    try:
        balance = res.json()['results']['0']['current']
    except:
        balance = None
    return str(balance)

def auth():
    print("Great! Let's get you started")
    print("Checking variables...")
    check_variables()
    print("All env variables are present!")
    print("We are going to authenticate you with Amex and Monzo!")
    print("Authenticating with Amex....")
    truelayer_auth_user()
    print("Thanks!")
    print("Trying to get access_token from truelayer!")
    truelayer_get_access_token()
    print("All good! Storing refresh code for later use...")
    print('Getting your Amex account_id...')
    truelayer_get_account_id()
    print("Done!")
    print("Amex is configured. Let's test!")
    print('Your balance is: ' + check_balance_for_testing_purposes())
    print("Although this is excluding pending transactions.")
    print("Now let's get Monzo connected!")
    get_new_monzo()
    print("All done!")
    print("Monzo and Amex are now connected. All you have to do is run script.py on a cronjob and it will automatically do the rest!")

def reauth():
    print("Welcome back!")
    print("I will check Amex to see if Amex need re-authenticating.")
    test = check_balance_for_testing_purposes()
    if test == None:
        print("Unable to connect to Amex. Re-authenticating Amex for good measure.")
        truelayer_auth_user()
        truelayer_get_access_token()
        truelayer_get_account_id()
        print("Done!")
        print('Rerun this script to auth Monzo!')
        exit()
    else:
        print("Amex is working so i assume you want to re-auth Monzo!")
        yesno = input("Do you want to proceed? (y/n): ")
        if yesno == "y":
            get_new_monzo()
            print("All done!")
            print("Monzo and Amex are now connected. All you have to do is run script.py on a cronjob and it will automatically do the rest!")
        else:
            exit()

