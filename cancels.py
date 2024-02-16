# script to monitor future reservations for cancels and to notify if they are cancelled
# we will run this every day
from database import Database
from utils import Utils
from network import Network
from proxies import Proxies
from discord import Discord
import schedule
import os
import time
from pytz import timezone
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

database = Database()
utils = Utils()
proxies = Proxies()
discord = Discord()


def init():
    # get all future reservations
    reservations = database.get_reservations(query={
        "cancelled": False, "date": {"$gt": datetime.now(timezone("EST")).strftime("%Y-%m-%d")},
    })

    utils.thread_success(f"Found {len(reservations)} reservation(s) to check for cancellation")

    x = 0
    delete_accs = 0
    cancelled_res = 0
    for res in reservations:
        network = Network(proxies.get_proxy())
        auth_token, payment_method_id = login(network, {"email": res["email"], "password": res["password"]})

        # account clipped
        if (auth_token is None) or (payment_method_id is None):
            # account is clipped, delete
            database.delete_account({"email": res["email"]})
            database.update_reservations(
                {"email": res["email"]}, {"$set": {"reviewed": True, "cancelled": True}}
            )
            utils.thread_error("Account has no valid login, cancelling")
            discord.cancels_wh(
                f"Cancelled a reservation for {res['email']} on {res['date']} at {res['venue_name']} [BadAccount]"
            )
            cancelled_res += 1
            delete_accs += 1
            x += 1
            utils.thread_warn(f"Checked reservation {x}/{len(reservations)}")
            continue

        acc_has_res = check_acc_has_res(network)

        if not acc_has_res:
            utils.thread_error("Account has no reservations, cancelling")
            database.update_reservations(
                {"email": res["email"]}, {"$set": {"reviewed": True, "cancelled": True}}
            )
            discord.cancels_wh(f"Cancelled a reservation for {res['email']} on {res['date']} at {res['venue_name']}")
            cancelled_res += 1

        x += 1
        utils.thread_success(f"Checked reservation {x}/{len(reservations)}")
    
    utils.thread_success(
        f"Finished checking {len(reservations)} accounts, deleted {delete_accs} (accounts), cancelled {cancelled_res}"
    )

def login(network, account, retrys=0):
    if retrys > 5:
        utils.thread_error("Login failed on max attempts, killing account")
        return None, None

    try:
        login_res = network.login(account["email"], account["password"])
    except Exception as e:
        utils.thread_error(f"Login failed with exception: {e}")
        time.sleep(network.ERROR_DELAY_LOGIN)
        return login(network, account, retrys=retrys + 1)

    if not login_res.ok:
        utils.thread_warn("Login failed")

        return login(network, account, retrys=retrys + 1)
    else:
        if retrys != 0:
            utils.thread_log("Successfully logged into anaccount after retry")

        retrys = 0

    auth_token = login_res.json()["token"]

    network.set_auth_token(auth_token)

    payment_method_id = login_res.json()["payment_method_id"]

    return auth_token, payment_method_id


def check_acc_has_res(network, retrys=0):
    if retrys > 5:
        return False

    try:
        account_check_res = network.account_reservations()
    except Exception as e:
        utils.thread_error(f"Failed to check account reservations with exception: {e}")
        return check_acc_has_res(network, retrys=retrys + 1)

    if not account_check_res.ok:
        utils.thread_error(f"Failed to check account reservations with exception: <{account_check_res.status_code}>")
        return check_acc_has_res(network, retrys=retrys + 1)

    if account_check_res.status_code == 200:
        if "reservations" in account_check_res.json():
            if len(account_check_res.json()["reservations"]) > 0:
                return True

    return False

if __name__ == '__main__':
    utils.thread_log("Script to check future reservations for cancels and to notify if they are cancelled")
    utils.thread_log("Running every day at 1am")
        
    schedule.every().day.at("01:00", "America/New_York").do(init)
    
    if os.getenv("DEBUG"):
        init()
    
    while True:
        schedule.run_pending()
        time.sleep(1)
