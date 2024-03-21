import requests
import os
from faker import Faker
from random import randint, choice
import secrets
import uuid
import string
from dotenv import load_dotenv
import urllib3
import threading
from termcolor import colored
import colorama
from database import Database
from network import Network
from aesCipher import AESCipher
from proxies import Proxies
from email_gen import EmailGen
import time
from wonderwords import RandomWord
import json
import sys
from utils import Utils

# CONFIG
# we dont care recursion gang
sys.setrecursionlimit(9999)

colorama.init()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

# LOAD IN CLASSES
utils = Utils()
database = Database()
proxies = Proxies()
fake = Faker()
email_gen = EmailGen()

if not os.getenv("ENCRYPTION_KEY"):
    utils.thread_error("No encryption key set")

aesCipher = AESCipher(os.getenv("ENCRYPTION_KEY"))

# GLOBALS
domains = []
if not os.getenv("DOMAINS"):
    utils.thread_error("No domains found, please set them in .env")
    sys.exit(1)
for domain in os.getenv("DOMAINS").split(","):
    domains.append(domain)
    
normal_cards = []
elite_cards = []

STRIPE_UA = "Resy/4977 CFNetwork/1492.0.1 Darwin/23.3.0"
STRIPE_P_UA = "stripe-ios/23.18.2; variant.legacy; PaymentSheet"

def gen(num_accs, acc_type, child=False):
    failure_cnt = 0

    try:
        cnt = 0
        for _ in range(num_accs):
            network = Network("")

            # Generate fake information
            first_name, last_name = gen_name()
            email = email_gen.gen(first_name, last_name, choice(domains))
            password = gen_password()
            phone_num = gen_phone_num()

            try:
                create_res = network.create(first_name, last_name, email, password, phone_num)
            except Exception as e:
                utils.thread_error(f"Error creating account: {e}")
                failure_cnt += 1
                continue

            if not create_res.ok:
                failure_cnt += 1
                continue

            auth_token = create_res.json()["user"]["token"]
            network.set_auth_token(auth_token)

            try:
                last_four = add_payment_info(network, auth_token, acc_type)
                if last_four is None:
                    failure_cnt += 1
                    continue

                write_account_to_db(
                    email, password, first_name, last_name, phone_num, acc_type, str(last_four)
                )
                cnt += 1

                utils.thread_success(f"Created account {cnt}/{num_accs} | {email}")
            except Exception as e:
                utils.thread_error(f"Error during or after adding payment info: {e}")
                failure_cnt += 1
                continue

        if failure_cnt > 0:
            gen(failure_cnt, acc_type, child=True)

        if not child:
            print()
            utils.thread_success(f"THREAD COMPLETE, QUITTING THREAD [{threading.active_count()}]")

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)

def write_account_to_db(email, password, first_name, last_name, phone_num, acc_type, last_four):
    account = {
        "email": email,
        "password": aesCipher.encrypt(password),
        "first_name": first_name,
        "last_name": last_name,
        "phone_num": phone_num,
        "acc_type": acc_type,
        "version": 1,
        "active": True,
        "suspended": False,
        "created_at": time.time(),
        "last_four": last_four
    }

    database.upload_account(account)

def gen_name():    
    name = fake.name()
    first_name = name.split(" ")[0]

    while len(first_name) <= 4:
        name = fake.name()
        first_name = name.split(" ")[0]

    last_name = name.split(" ")[1]

    return first_name, last_name


def gen_password():
    special_chars = ["$", "?", "!"]
    alphabet = string.ascii_letters + string.digits
    password = "".join(secrets.choice(alphabet) for i in range(randint(16, 20)))

    return f"{choice(special_chars)}{password}{randint(100, 999)}"


def gen_phone_num():
    f = Faker(locale="en_US")
    phone_num = f.phone_number()
    if "x" in phone_num:
        phone_num = phone_num.split("x")[0]
    phone_num = phone_num.replace(".", "")
    phone_num = phone_num.replace("-", "")
    phone_num = phone_num.replace("(", "")
    phone_num = phone_num.replace(")", "")
    phone_num = phone_num.replace("+1", "")

    nyc_codes = ["917", "347", "212", "646"]
    use_nyc_codes_odds = randint(0, 100)
    if use_nyc_codes_odds > 60:
        phone_num = phone_num.replace(phone_num[0:3], choice(nyc_codes), 1)
        
    return phone_num

def add_payment_info(network, token, acc_type):
    if acc_type == "normal":
        card = choice(normal_cards)
    elif acc_type == "elite":
        card = choice(elite_cards)
    
    card_parts = card.split("|")
    
    if len(card_parts) != 5:
        utils.thread_error(f"Invalid card format [{card}], killing process")
        return sys.exit(1)
        
    card_num = card_parts[0]
    card_month = card_parts[1]
    card_year = card_parts[2]
    card_cvc = card_parts[3]
    card_zip = card_parts[4]
    
    url = "https://api.resy.com/3/stripe/setup_intent"

    headers = {
        "host": "api.resy.com",
        "accept": "*/*",
        "connection": "keep-alive",
        "x-resy-auth-token": token,
        "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        "x-resy-universal-auth": token,
        "user-agent": network.USER_AGENT,
        "accept-language": "en-US;q=1.0, fr-US;q=0.9",
        "authorization": network.RESY_KEY,
    }

    try:
        res1 = requests.post(url, headers=headers, proxies=proxies.get_proxy(), verify=False, timeout=10)
    except Exception as e:
        utils.thread_error(f"Error adding payment info 1: {e}")
        return None

    if not res1.ok:
        utils.thread_error(f"Error adding payment info 1: {res1.status_code}")
        return None

    client_secret = res1.json()["client_secret"]
    client_id = client_secret.split("_secret")[0]

    url2 = f"https://api.stripe.com/v1/setup_intents/{client_id}/confirm"

    headers2 = {
        "host": "api.stripe.com",
        "content-type": "application/x-www-form-urlencoded",
        "accept-encoding": "gzip, deflate, br",
        "stripe-version": "2020-08-27",
        "user-agent": "Resy/5185 CFNetwork/1492.0.1 Darwin/23.3.0",
        "connection": "keep-alive",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "x-stripe-user-agent": '{"os_version":"17.3.1","bindings_version":"23.21.0","lang":"objective-c","type":"iPhone16,2","model":"iPhone","vendor_identifier":"521D44E8-0B56-460D-95A4-D74D91611B1F"}',
        "authorization": "Bearer pk_live_51JdK5FIqT2RuI7QtpZsqeG1GTMZHBTBCTr4r1MZkJJt60ybz3REl92I0uKIynSMIUMXkUlMGAU8B5pRJ0533KImO0006EPpHUI",
    }
    
    payload2 = {
        "client_secret": client_secret,
        "expand[0]": "payment_method",
        "payment_method_data[billing_details][address][country]": "US",
        "payment_method_data[billing_details][address][postal_code]": card_zip,
        "payment_method_data[card][cvc]": card_cvc,
        "payment_method_data[card][exp_month]": card_month,
        "payment_method_data[card][exp_year]": card_year,
        "payment_method_data[card][number]": card_num,
        "payment_method_data[payment_user_agent]": "stripe-ios/23.21.0; variant.legacy; PaymentSheet",
        "payment_method_data[type]": "card",
        "use_stripe_sdk": "true",
    }

    try:
        res2 = requests.post(url2, headers=headers2, data=payload2, timeout=10)
    except Exception as e:
        utils.thread_error(f"Error adding payment info 2: {e}")
        return None

    if not res2.ok:
        utils.thread_error(f"Error adding payment info 2: {res2.status_code}")
        return None

    payment_method_id = res2.json()["payment_method"]
    url3 = "https://api.resy.com/3/stripe/payment_method"
    payload3 = f"is_default=1&stripe_payment_method_id={payment_method_id['id']}"
    headers = {
        "host": "api.resy.com",
        "content-type": "application/x-www-form-urlencoded; charset=utf-8",
        "accept": "*/*",
        "connection": "keep-alive",
        "x-resy-auth-token": token,
        "accept-language": "en-US;q=1.0, fr-US;q=0.9",
        "x-resy-universal-auth": token,
        "user-agent": "Resy/2.78 (com.resy.ResyApp; build:5185; iOS 17.3.1) Alamofire/5.8.0",
        "authorization": 'ResyAPI api_key="AIcdK2rLXG6TYwJseSbmrBAy3RP81ocd"',
        "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
    }

    try:
        res3 = requests.post(url3, headers=headers, data=payload3, proxies=proxies.get_proxy(), verify=False, timeout=10)
    except Exception as e:
        utils.thread_error(f"Error adding payment info 3: {e}")
        return None

    if not res3.ok:
        utils.thread_error(f"Error adding payment info 3: {res3.status_code, res3.text}")
        return None

    return os.getenv("CARD_NUM")[-4:]

def load_cards():
    if not os.path.isfile("./normal_cards.txt"):
        utils.thread_error("No normal_cards.txt found")
        sys.exit(1)
        
    with open("normal_cards.txt", "r") as f:
        for line in f.readlines():
            normal_cards.append(line.strip())
    
    if not os.path.isfile("./elite_cards.txt"):
        utils.thread_error("No elite_cards.txt found")
        sys.exit(1)
    
    with open("elite_cards.txt", "r") as f:
        for line in f.readlines():
            elite_cards.append(line.strip())

def 

if __name__ == "__main__":
    # Intro print
    print()
    utils.thread_log("Resy Account Generator")
    utils.thread_log("For use for ResMe research purposes only")
    print()
    utils.thread_error("!!! MAKE SURE YOU HAVE A VPN ENABLED !!!")
    print()
    print("*" * 80)
    print()
    
    load_cards()

    num_accs_normal = int(input("How many NORMAL accounts to create per thread?: "))
    num_accs_elite = int(input("How many ELITE accounts to create per thread?: "))
    num_threads = int(input("Number of threads?: "))
    print()
    
    cnt = 0
    if num_accs_normal > 0:
        for _ in range(num_threads):
            thread_id = f"Gen Normal {cnt + 1}"
            
            
            threading.Thread(
                target=gen,
                name=thread_id,
                args=(
                    num_accs_normal,
                    "normal",
                ),
            ).start()
            
            utils.thread_warn(f"Starting normal gen thread {thread_id}")
            time.sleep(0.5)
            cnt += 1
    
    if num_accs_elite > 0:
        for _ in range(num_threads):
            thread_id = f"Gen Elite {cnt + 1}"
            
            threading.Thread(
                target=gen,
                name=thread_id,
                args=(
                    num_accs_elite,
                    "elite",
                ),
            ).start()
            
            utils.thread_warn(f"Starting elite gen thread {thread_id}")
            time.sleep(0.5)
            cnt += 1
