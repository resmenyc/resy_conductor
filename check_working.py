from database import Database
import sys
import time
from utils import Utils
from proxies import Proxies
import threading
from network import Network
from random import shuffle
import schedule
from discord_helper import Discord
import os

database = Database()
utils = Utils()
proxies = Proxies()
discord = Discord()
accounts = database.get_accounts()
shuffle(accounts)

THREAD_CNT = 50

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
                utils.thread_warn("Marking account as not usable")
                # account isnt usable, make sure we mark as such
                database.update_account(
                    {"email": account["email"]}, {"$set": {"active": False}}
                )
            else:
                database.update_account(
                    {"email": account["email"]}, {"$set": {"active": True}}
                )

            num += 1
            utils.thread_success(f"Checked account {num}/{len(accs)} [{payment_method_id}]")
            # time.sleep(1)

        print()
        end_msg = f"Finished checking {len(accounts)} accounts, deleted {delete_accs}"
        utils.thread_success(end_msg)
        try:
            discord.logs_wh(end_msg)
        except:
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

def login(network, account, retrys=0, rl=0):
    if retrys > 30:
        utils.thread_error("Login failed on max attempts, killing account")
        return None, None, None

    try:
        login_res = network.login(account["email"], account["password"])
    except Exception as e:
        utils.thread_error(f"Login failed with exception: {e}")
        time.sleep(network.ERROR_DELAY_LOGIN)
        return login(network, account, retrys=retrys + 1, rl=rl)

    if not login_res.ok:
        if login_res.status_code == 419:
            utils.thread_warn(f"Account suspended {account['email']}")
        elif login_res.status_code == 500:
            utils.thread_warn(f"RATE LIMIT {rl}")
            return login(network, account, retrys=retrys, rl=rl + 1)
        else:
            utils.thread_error(f"Login failed with status code {login_res.status_code}, retrying")
            return login(network, account, retrys=retrys + 1, rl=rl)

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

def check_acc_usable(network, retrys=0):
    if retrys > 5:
        return False
    
    try:
        account_check_res = network.account_reservations()
    except:
        time.sleep(1)
        return check_acc_usable(network, retrys=retrys + 1)

    if not account_check_res.ok:
        return False

    if account_check_res.status_code == 200:
        if "reservations" in account_check_res.json():
            if len(account_check_res.json()["reservations"]) == 0:
                return True
    else:
        return False

# https://stackoverflow.com/questions/2130016/splitting-a-list-into-n-parts-of-approximately-equal-length
def split_list(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))

def init():    
    # Split the list into thread_cnt lists
    print()
    utils.thread_success(f"Initiating with {THREAD_CNT} thread(s)")
    print()
    
    acc_lsts = list(split_list(accounts, THREAD_CNT))
        
    cnt = 0
    for acc_lst in acc_lsts:
        tread_id = f"Thread{cnt}"
        threading.Thread(
            target=check_working,
            args=(acc_lst,),
            name=tread_id
        ).start()
        
        time.sleep(0.5)
        cnt += 1

if __name__ == "__main__":
    utils.thread_log("Script to iterate over the DB and check all the accounts\n")
    utils.thread_log("Running every wednesday at 2:00am")

    schedule.every().wednesday.at("02:00", "America/New_York").do(init)
    schedule.every().monday.at("02:00", "America/New_York").do(init)
    schedule.every().friday.at("02:00", "America/New_York").do(init)

    if os.getenv("DEBUG"):
        init()

    while True:
        schedule.run_pending()
        time.sleep(1)
