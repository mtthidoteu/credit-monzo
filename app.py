from peewee import *
from dotenv import load_dotenv

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