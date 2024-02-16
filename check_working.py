from database import Database
import sys
import time
from utils import Utils
from proxies import Proxies
import threading
from network import Network
from random import shuffle
import schedule
import os

database = Database()
utils = Utils()
proxies = Proxies()
accounts = database.get_accounts()
shuffle(accounts)

def check_working(accs):
    try:
        num = 0
        delete_accs = 0
        for account in accs:
            # patch bad names
            if len(account["first_name"]) <= 4:
                database.delete_account({"email": account["email"]})
                num += 1
                continue

            if "-" in account["email"]:
                database.delete_account({"email": account["email"]})
                num += 1
                continue                

            network = Network(proxies.get_proxy())
            auth_token, payment_method_id, is_acc_usable = login(network, account)

            if (auth_token is None) or (payment_method_id is None):
                # account is clipped, delete
                database.delete_account({"email": account["email"]})
                database.update_reservations(
                    {"email": account["email"]}, {"$set": {"reviewed": True, "cancelled": True}}
                )
                utils.thread_error("Deleting account...")
                delete_accs += 1
            elif not is_acc_usable:
                # account isnt usable, make sure we mark as such
                database.update_account(
                    {"email": account["email"]}, {"$set": {"active": False}}
                )
            else:
                database.update_account(
                    {"email": account["email"]}, {"$set": {"active": True}}
                )

            num += 1
            utils.thread_success(f"Checked account {num}/{len(accs)}")
            # time.sleep(1)

        print()
        utils.thread_success(f"Finished checking {len(accounts)} accounts, deleted {delete_accs}")
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

def login(network, account, retrys=0):
    if retrys > 20:
        utils.thread_error("Login failed on max attempts, killing account")
        return None, None, None

    try:
        login_res = network.login(account["email"], account["password"])
    except Exception as e:
        utils.thread_error(f"Login failed with exception: {e}")
        time.sleep(network.ERROR_DELAY_LOGIN)
        return login(network, account, retrys=retrys + 1)

    if not login_res.ok:
        utils.thread_warn("Login failed")

        return None, None, None
    else:
        if retrys != 0:
            utils.thread_log("Successfully logged into anaccount after retry")

        retrys = 0

    auth_token = login_res.json()["token"]

    network.set_auth_token(auth_token)

    payment_method_id = login_res.json()["payment_method_id"]

    is_acc_usable = check_acc_usable(network)

    return auth_token, payment_method_id, is_acc_usable

def check_acc_usable(network):
    account_check_res = network.account_reservations()

    if not account_check_res.ok:
        return False

    if account_check_res.status_code == 200:
        if "reservations" in account_check_res.json():
            if len(account_check_res.json()["reservations"]) == 0:
                return True
    else:
        return False

# https://stackoverflow.com/questions/752308/split-list-into-smaller-lists-split-in-half
def split_list(a_list):
    half = len(a_list) // 2
    return a_list[:half], a_list[half:]


def init():
    accs1234, accs5678 = split_list(accounts)
    accs12, accs34 = split_list(accs1234)
    accs56, accs78 = split_list(accs5678)
    accs1, accs2 = split_list(accs12)
    accs3, accs4 = split_list(accs34)
    accs5, accs6 = split_list(accs56)
    accs7, accs8 = split_list(accs78)

    t1 = threading.Thread(target=check_working, args=(accs1,), name="Thread1")
    t2 = threading.Thread(target=check_working, args=(accs2,), name="Thread2")
    t3 = threading.Thread(target=check_working, args=(accs3,), name="Thread3")
    t4 = threading.Thread(target=check_working, args=(accs4,), name="Thread4")
    t5 = threading.Thread(target=check_working, args=(accs5,), name="Thread5")
    t6 = threading.Thread(target=check_working, args=(accs6,), name="Thread6")
    t7 = threading.Thread(target=check_working, args=(accs7,), name="Thread7")
    t8 = threading.Thread(target=check_working, args=(accs8,), name="Thread8")

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    t8.start()

if __name__ == "__main__":
    utils.thread_log("Script to iterate over the DB and check all the accounts\n")
    utils.thread_log("Running every sunday and wed at 2:00am")

    schedule.every().wednesday.at("02:00", "America/New_York").do(init)
    schedule.every().sunday.at("02:00", "America/New_York").do(init)
    
    if os.getenv("DEBUG"):
        init()

    while True:
        schedule.run_pending()
        time.sleep(1)
