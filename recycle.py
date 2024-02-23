from database import Database
import time
from utils import Utils
from random import shuffle
import schedule
import os
from discord_helper import Discord

SUSPEND_FACTOR = 4

database = Database()
utils = Utils()
discord = Discord()

def init():
    utils.thread_log("Running recycle script")
    # take 1/SUSPEND_FACTOR of the accounts and suspend them, take every suspended account and unsuspend
    accounts = database.get_accounts({"suspended": False, "active": True})

    database.update_accounts({"suspended": True}, {"$set": {"suspended": False}})

    shuffle(accounts)

    new_suspended_emails = []
    x = 0
    for account in accounts[:len(accounts)//SUSPEND_FACTOR]:
        new_suspended_emails.append(account["email"])
        x += 1
        utils.thread_log(f"Suspended account {x}/{len(accounts)//SUSPEND_FACTOR}")
    
    database.update_accounts({"email": {"$in": new_suspended_emails}}, {"$set": {"suspended": True}})


    end_msg = f"Successfully marked {len(accounts)//SUSPEND_FACTOR} accounts as suspended and unsuspended old accounts"
    utils.thread_success(f"\n{end_msg}")
    discord.logs_wh(end_msg)

def unsuspend_all():
    database.update_accounts({}, {"$set": {"suspended": False}})

if __name__ == '__main__':
    utils.thread_log(f"Script to randomly suspend accounts | Factor {SUSPEND_FACTOR}")
    utils.thread_log("Running every day at 3am")

    schedule.every().day.at("03:00", "America/New_York").do(init)
    
    if os.getenv("DEBUG"):
        init()
    
    while True:
        schedule.run_pending()
        time.sleep(1)
