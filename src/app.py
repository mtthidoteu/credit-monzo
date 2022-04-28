from peewee import *
from dotenv import load_dotenv
import os

load_dotenv()

database = SqliteDatabase(os.getenv("database_file"))

class BaseModel(Model):
    class Meta:
        database = database


class Transactions(BaseModel):
    id = AutoField()
    amount = FloatField(null=True)
    description = TextField(null=True)
    monzoed = IntegerField(null=True)
    timestamp = TextField(null=True)


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
