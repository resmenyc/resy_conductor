# Collection of DB calls and helpers

from pymongo import MongoClient
import os
from bson.json_util import dumps, loads
from aesCipher import AESCipher
from dotenv import load_dotenv
import sys
from utils import Utils

load_dotenv()

aesCiper = AESCipher(os.getenv("ENCRYPTION_KEY"))
utils = Utils()


class Database:
    def __init__(self):
        if not os.getenv("DB_URL"):
            utils.thread_error("DB_URL not set")
            return sys.exit(1)

        self.db = MongoClient(host=os.getenv("DB_URL"))

    def get_db(self):
        return self.db.resme

    def get_accounts(self, query={}):
        # TODO: only load accounts marked as usable
        accs = self.get_db().resy_accounts.find(query)
        accs = loads(dumps(accs))

        for acc in accs:
            acc["password"] = aesCiper.decrypt(acc["password"])

        return accs

    def delete_account(self, query):
        collection = self.get_db().resy_accounts
        collection.delete_one(query)

    def update_account(self, query, exec):
        collection = self.get_db().resy_accounts
        collection.update_one(query, exec)

    def update_accounts(self, query, exec):
        collection = self.get_db().resy_accounts
        collection.update_many(query, exec)

    def upload_account(self, account):
        collection = self.get_db().resy_accounts
        collection.insert_one(account)

    def get_reservations_safe(self, query={}):
        ress = self.get_db().resy_reservations.find(query)
        ress = loads(dumps(ress))

        return ress

    def get_reservations(self, query={}):
        ress = self.get_db().resy_reservations.find(query)
        ress = loads(dumps(ress))

        for res in ress:
            res["password"] = aesCiper.decrypt(res["password"])

        return ress

    def update_reservation(self, query, exec):
        collection = self.get_db().resy_reservations
        collection.update_one(query, exec)

    def update_reservations(self, query, exec):
        collection = self.get_db().resy_reservations
        collection.update_many(query, exec)
