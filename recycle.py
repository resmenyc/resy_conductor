from database import Database
import time
from utils import Utils
from random import shuffle
import schedule
import os

SUSPEND_FACTOR = 4

database = Database()
utils = Utils()

def init():
    utils.thread_log("Running recycle script")
    # take 1/SUSPEND_FACTOR of the accounts and suspend them, take every suspended account and unsuspend
    accounts = database.get_accounts({"suspended": False, "active": True})

    database.update_accounts({"suspended": True}, {"$set": {"suspended": False}})
    
    shuffle(accounts)

    x = 0
    for account in accounts[:len(accounts)//SUSPEND_FACTOR]:
        database.update_account({"email": account["email"]}, {"$set": {"suspended": True}})
        x += 1
        utils.thread_log(f"Suspended account {x}/{len(accounts)//SUSPEND_FACTOR}")

    utils.thread_success(f"Successfully marked {len(accounts)//SUSPEND_FACTOR} accounts as suspended and unsuspended old accounts")

def unsuspend_all():
    database.update_accounts({}, {"$set": {"suspended": False}})

if __name__ == '__main__':
    utils.thread_log(f"Script to randomly suspend accounts | Factor {SUSPEND_FACTOR}")
    utils.thread_log("Running every day at 2am")

    schedule.every().day.at("02:00", "America/New_York").do(init)
    
    if os.getenv("DEBUG"):
        init()
    
    while True:
        schedule.run_pending()
        time.sleep(1)
