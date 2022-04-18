from peewee import *
from dotenv import load_dotenv
import sys
from datetime import datetime
import auth
import script


load_dotenv()

database = SqliteDatabase("./database.db")

class BaseModel(Model):
    class Meta:
        database = database


class Transactions(BaseModel):
    id = AutoField()
    transaction_id = IntegerField(null=True)
    amount = FloatField(null=True)
    description = TextField(null=True)
    monzoed = IntegerField(null=True)


class Data(BaseModel):
    key = TextField()
    value = TextField(null=True)

# Below is Database Initialisation in case of new instance
def all_subclasses(base: type) -> list[type]:
    return [
        cls
        for sub in base.__subclasses__()
        for cls in [sub] + all_subclasses(sub)
    ]


try:
    models = [
        sub for sub in all_subclasses(Model)
        if not sub.__name__.startswith('_')
    ]

    database.create_tables(models)
except:
    pass

command = sys.argv[1]

if command == "run":
    if not script.get_transactions():
        print("Refreshing Truelayer token!")
        script.get_refresh_token()
        if not script.get_transactions():
           script.warn("truelayer")
        else:
            if not script.monzo_them():
                script.monzo_refresh_token()
                if not script.monzo_them():
                    script.warn("monzo")   
    else:
        if not script.monzo_them():
            script.monzo_refresh_token()
            if not script.monzo_them():
                script.warn("monzo")

elif command == "auth":
    print("Welcome to the amex-monzo authenticaton script!")
    arg = input("Is this your first time? (yes/no): ")
    if arg == "yes":
        auth.auth()
    elif arg == "no":
        auth.reauth()
    else:
        print("Invalid Input")
else:
    print(f"Invalid Usage: python {sys.argv[0]} run|auth")
    exit()
