
# Amex-Monzo

A script to synchronise Credit Card Transactions and Monzo, which can be setup to be run every 15 minutes via cron.
#### Requirements
- Monzo Account
- Support Credit Card 
- Python >3.9 (Virtual Env is recommended!)

### Supported Credit Card
- American Express
- Barclaycard (untested*)
- Capital One (untested*)
- Tesco Bank (untested*)

I haven't personally tested all of these but I don't see why it shouldn't work! The truelayer api is pretty straightforward


| :exclamation:  Attention :exclamation:  |
|-----------------------------------------|
The issue with the refresh token I had highlighted was in fact a misconfiguration! When you are creating your Monzo 'client', make sure to make it 'Confidential"!

#### Work In progress
- GUI for setting up and monitoring


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

- `truelayer_client_id`

- `truelayer_client_secret`

- `monzo_client_id`

- `monzo_client_secret`

- `pot_id`

- `monzo_account_id`

- `database_file`


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
- In Monzo Developers, create a Client with `Redirect URL` set to `http://127.0.0.1:5000/callback` and 'Confidentiality' set to 'Confindetial'!
- Add newly created Client ID and Client Secret to `.env`
- Install dependencies

```bash
  pip install -r requirements.txt
```
-  Run authentication script
```bash
  python script.py auth
```
- Following Instructions carefully! Make sure to read each line!
- If the script has succeeded, you should be good to go!

## Running
Once the setup has been completed. You should be able to run a synchronisation by running

```bash
python script.py run
```
This will download all your 'pending transactions' from your Amex account and add them to our database. It will then deposit that amount into a pot!

## Making script run dynamically

You will probably have noticed but this script doesn't monitor transactions it only checks the transactions **once** and exists. What I would recommend if having a cronjob or something similar have the script run every 15 minutes for instance.

For example:

```cron
*/15 * * * * /path/to/python/or/venv /path/to/cloned/repository/app.py run
```


## FAQ

#### I am getting Error TypeError: 'type' object is not subscriptable

Please upgrade to > Python3.9

#### How will I know if my tokens have expired?

Currently I haven't implemented a very good error notification system and the script won't really throw errors. It'll just keep trying. However, if you notice it stops working, re-run `python script.py auth`

## License
[Common Clause](https://commonsclause.com)
