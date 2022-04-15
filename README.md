
# Amex-Monzo

A script to synchronise Amex Transactions and Monzo, which can be setup to be run every 15 minutes via cron.
#### Requirements
- Monzo Account
- American Express Account 


| :exclamation:  This is very important   |
|-----------------------------------------|
Monzo needs to fix their refresh_tokens so unfortunately, until they do so, the script will only work for 24 hours at a time. [Please help me draw attention to this here.](https://community.monzo.com/t/exchanging-authorisation-code-giving-everything-except-refresh-token/131532)




## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

- `truelayer_client_id`

- `truelayer_client_secret`

- `monzo_client_id`

- `monzo_client_secret`

- `pot_id`

- `monzo_account_id`


## Installation and Setup

- On your Monzo App, create an American Express Pot

Clone the project into directory

```bash
  git clone https://github.com/mtthidoteu/amex-monzo.git
```

- Create a TrueLayer Account
- Make sure you are in 'LIVE' Mode (upright toggle)
- Create Data API **Client_ID** and **client_secret** add add to `.env` file
- Login to [Monzo Developers](https://developers.monzo.com) and login with Monzo Account
- In Monzo Playground, make a GET request to `/pots?current_account_id=$account_id`
- Locate and Add your Amex Pot's ID into `.env`
- Make note of your 'account_id' and add it to `.env`
- In Monzo Developers, create a Client with `Redirect URL` set to `http://localhost:5000/callback`
- Add newly created Client ID and Client Secret to `.env`
- Install dependencies

```bash
  pip install -r requirements.txt
```
-  Run authentication script
```bash
  python auth.py
```
- Following Instructions carefully! Make sure to read each line!
- If the script has succeeded, you should be good to go!

## Running
Once the setup has been completed. You should be able to run a synchronisation by running

```bash
python script.py
```
This will download all your 'pending transactions' from your Amex account and add them to our database. It will then deposit that amount into a pot!

## Making script run dynamically

You will probably have noticed but this script doesn't monitor transactions it only checks the transactions **once** and exists. What I would recommend if having a cronjob or something similar have the script run every 15 minutes for instance.

For example:

```cron
*/15 * * * * /path/to/python/or/venv /path/to/cloned/repository/script.py
```