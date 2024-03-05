import requests
import os
from faker import Faker
from datetime import datetime
from random import randint, choice
import secrets
import uuid
import string
from dotenv import load_dotenv
import urllib3
import multiprocessing
import threading
from termcolor import colored
import colorama
from database import Database
from aesCipher import AESCipher
from proxies import Proxies
import time
from wonderwords import RandomWord
import json
import urllib3
import sys

sys.setrecursionlimit(9999)

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"

colorama.init()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
database = Database()
proxies = Proxies()
aesCipher = AESCipher(os.getenv("ENCRYPTION_KEY"))
domains = []

RESY_UA = "Resy/2.77 (com.resy.ResyApp; build:5035; iOS 17.3.0) Alamofire/5.8.0"
STRIPE_UA = "Resy/4977 CFNetwork/1492.0.1 Darwin/23.3.0"
STRIPE_P_UA = "stripe-ios/23.18.2; variant.legacy; PaymentSheet"


def gen_email(first_name, last_name, fake_domain):
    fake = Faker()
    faker_email = fake.email()

    base_email_prefix = faker_email.split("@")[0]
    email = f"{first_name}{base_email_prefix}{randint(10, 999)}@{fake_domain}".lower()

    return email


def gen_email_2(first_name, last_name, fake_domain):
    return f"{first_name}.{last_name}{randint(10, 999)}@{fake_domain}".lower()


def gen_email_3(first_name, last_name, fake_domain):
    fake = Faker()
    faker_email = fake.email()

    base_email_prefix = faker_email.split("@")[0]
    email = f"{last_name}{base_email_prefix}{randint(1, 99)}@{fake_domain}".lower()

    return email

def gen_email_4(first_name, last_name, fake_domain):
    return f"{first_name}{RandomWord().word()}{randint(1, 999)}@{fake_domain}".lower()

def gen_email_5(first_name, last_name, fake_domain):
    first_initial = first_name[:1]
    return f"{first_initial}{last_name}{randint(10, 999)}@{fake_domain}".lower()

def gen_email_6(first_name, last_name, fake_domain):
    last_initial = last_name[:1]
    return f"{first_name}{last_initial}{randint(10, 999)}@{fake_domain}".lower()

def gen_email_7(first_name, last_name, fake_domain):
    return gen_email_8(first_name, last_name, fake_domain)


def gen_email_8(first_name, last_name, fake_domain):
    return f"{RandomWord().word()}{last_name}{randint(1, 999)}@{fake_domain}".lower()


def gen_email_11(first_name, last_name, fake_domain):
    return f"{first_name}{RandomWord().word()}{randint(1, 999)}@{fake_domain}".lower()

def gen_email_12(first_name, last_name, fake_domain):
    return f"{first_name}.{RandomWord().word()[:1].lower()}.{last_name}{randint(1, 99)}@{fake_domain}".lower()

def gen_email_13(first_name, last_name, fake_domain):
    return f"{first_name}{RandomWord().word()[:1].lower()}{last_name}{randint(1, 99)}@{fake_domain}".lower()

def gen_email_9(first_name, last_name, fake_domain):
    return f"{RandomWord().word()}{RandomWord().word()}{first_name[:1].upper()}{last_name[:1].upper()}{randint(1, 99)}@{fake_domain}".lower()


def gen_email_14(first_name, last_name, fake_domain):
    return f"{RandomWord().word()}{RandomWord().word()}{first_name[:1].upper()}{last_name[:1].upper()}{randint(1, 99)}@{fake_domain}".lower()

def gen_email_15(first_name, last_name, fake_domain):
    fake = Faker()
    base_string = f"{fake.profile()['username']}"
    return f"{base_string.lower()}{first_name}{randint(1, 99)}@{fake_domain}".lower()

def gen_email_10(first_name, last_name, fake_domain):
    fake = Faker()
    base_string = f"{fake.profile()['username']}"

    cases = [1, 2, 4, 5, 6]
    chosen_case = choice(cases)

    if chosen_case == 1:
        return f"{base_string}{randint(1, 999)}@{fake_domain}".lower()
    elif chosen_case == 2:
        return f"{base_string}{randint(1, 999)}@{fake_domain}".lower()
    elif chosen_case == 4:
        return f"{first_name[:1].upper()}{base_string.lower()}{randint(10, 99)}@{fake_domain.lower()}"
    elif chosen_case == 5:
        return f"{first_name[:1]}{last_name}{base_string.lower()}@{fake_domain.lower()}"
    elif chosen_case == 6:
        return f"{first_name[:1]}{last_name}{base_string.lower()}{randint(1, 999)}@{fake_domain.lower()}"

# TODO:add weights to each one
gen_email_methods = [gen_email, gen_email_2, gen_email_4, gen_email_5, gen_email_6, gen_email_7, gen_email_8, gen_email_9, gen_email_10, gen_email_11, gen_email_12, gen_email_13, gen_email_14, gen_email_15]

# TODO add weights to each one
for _ in range(4):
    gen_email_methods.append(gen_email_10)

def thread_log(message):
    msg = f"[{threading.current_thread().name}] <{datetime.utcnow()}> {message}"

    print(colored(msg, "cyan"))


def thread_error(message):
    msg = f"[{threading.current_thread().name}] <{datetime.utcnow()}> {message}"

    print(colored(msg, "red"))


def thread_warn(message):
    msg = f"[{threading.current_thread().name}] <{datetime.utcnow()}> {message}"

    print(colored(msg, "yellow"))


def thread_success(message):
    msg = f"[{threading.current_thread().name}] <{datetime.utcnow()}> {message}"

    print(colored(msg, "green"))


def thread_print(message):
    print(f"[{threading.current_thread().name}] <{datetime.utcnow()}> {message}")


def gen_password():
    alphabet = string.ascii_letters + string.digits
    password = "".join(secrets.choice(alphabet) for i in range(randint(16, 20)))

    return f"${password}111"


def gen(num_accs, acc_type):
    try:
        x = 0
        for i in range(num_accs):
            s = requests.Session()

            fake_domain = choice(domains)
            fake = Faker()
            name = fake.name()
            first_name = name.split(" ")[0]

            while len(first_name) <= 4:
                name = fake.name()
                first_name = name.split(" ")[0]

            last_name = name.split(" ")[1]

            # TODO: add more ways to do this so they arent all templated the same
            email_method = choice(gen_email_methods)
            email = email_method(first_name, last_name, fake_domain)
            password = gen_password()

            phone_num = gen_phone_num()

            try:
                token = create(s, first_name, last_name, email, password, phone_num)
            except Exception as e:
                thread_error(e)
                x+= 1
                threading.Thread(
                    target=gen,
                    name=f"SomeTryAgainThread",
                    args=(
                        1,
                        acc_type,
                    ),
                ).start()
                continue

            if token != None:
                try:
                    add_payment_info(s, token)
                    write_account_to_db(
                        email, password, first_name, last_name, phone_num, acc_type
                    )
                    x += 1
                    print()
                    if (x != 1) and {num_accs != 1}:
                        thread_success(f"Generated Account {x}/{num_accs} [{email}]")
                        print()
                except Exception as e:
                    print(e)
                    thread_error("Error adding payment info")
                    print()
                    x += 1
                    t = threading.Thread(
                        target=gen,
                        name=f"SomeTryAgainThread",
                        args=(
                            1,
                            acc_type,
                        ),
                    ).start()
                    continue
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)

    
    if num_accs != 1:
        print()
        thread_success(f"THREAD COMPLETE, QUITTING THREAD [{threading.active_count()}]")

def gen_phone_num():
    fake = Faker()
    phone_num = fake.phone_number()
    if "x" in phone_num:
        phone_num = phone_num.split("x")[0]
    phone_num = phone_num.replace(".", "")
    phone_num = phone_num.replace("-", "")
    phone_num = phone_num.replace("(", "")
    phone_num = phone_num.replace(")", "")
    
    nyc_codes = ["917", "347", "212", "646"]
    use_nyc_codes_odds = randint(0, 100)
    if use_nyc_codes_odds > 70:
        phone_num = phone_num.replace(phone_num[0:3], choice(nyc_codes), 1)

    # replace the first three characters with 212
    # phone_num = phone_num.replace(phone_num[0:3], "347", 1)

    return phone_num


def write_account_to_db(email, password, first_name, last_name, phone_num, acc_type):
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
    }

    database.upload_account(account)


def write_account_to_file(email, password, first_name, last_name, phone_num):
    with open("accs.txt", "a+") as f:
        f.write(f"{email}|{password}|{first_name}|{last_name}|{phone_num}\n")


def create(s, first_name, last_name, email, password, phone_num):
    retry_cnt = 0
    url = "https://api.resy.com/2/user/registration"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": 'ResyAPI api_key="AIcdK2rLXG6TYwJseSbmrBAy3RP81ocd"',
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": RESY_UA,
        "Origin": "https://resy.com"
    }

    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "mobile_number": f"+1{gen_phone_num()}",
        "em_address": email,
        "policies_accept": 1,
        "marketing_opt_in": 0,
        "complete": 1,
        "device_type_id": 3,
        "device_token": str(uuid.uuid4()),
        "isNonUS": 0,
        "password": password
    }

    res = s.post(url, headers=headers, data=payload, proxies=proxies.get_proxy(), verify=False, timeout=10)
    if res.status_code != 201:
        # print("Retrying...", res.text)
        phone_num = gen_phone_num()
        return create(
            s,
            first_name,
            last_name,
            email,
            password,
            phone_num,
        )

    auth_token = res.json()["user"]["token"]

    return auth_token


def add_payment_info(s, token):
    url = "https://api.resy.com/3/stripe/setup_intent"

    headers = {
        "host": "api.resy.com",
        "accept": "*/*",
        "x-resy-auth-token": token,
        "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        "x-resy-universal-auth": token,
        "user-agent": RESY_UA,
        "accept-language": "en-US;q=1.0",
        "authorization": 'ResyAPI api_key="AIcdK2rLXG6TYwJseSbmrBAy3RP81ocd"',
    }

    try: 
        res = s.post(url, headers=headers, proxies=proxies.get_proxy(), verify=False, timeout=10)
    except Exception as e:
        thread_error(e)
        time.sleep(1)
        print(e, "retrying")
        return add_payment_info(s, token)

    client_secret = res.json()["client_secret"]
    client_id = client_secret.split("_secret")[0]

    url2 = f"https://api.stripe.com/v1/setup_intents/{client_id}/confirm"

    payload2 = {
        "client_secret": client_secret,
        "payment_method_data[billing_details][address][country]": "US",
        "payment_method_data[billing_details][address][postal_code]": os.getenv(
            "ZIP_CODE"
        ),
        "payment_method_data[card][cvc]": os.getenv("CARD_CVC"),
        "payment_method_data[card][exp_month]": os.getenv("CARD_MONTH"),
        "payment_method_data[card][exp_year]": os.getenv("CARD_YEAR"),
        "payment_method_data[card][number]": os.getenv("CARD_NUM"),
        "payment_method_data[payment_user_agent]": STRIPE_P_UA,
        "payment_method_data[type]": "card",
        "use_stripe_sdk": "true",
    }

    headers2 = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": "Bearer pk_live_51JdK5FIqT2RuI7QtpZsqeG1GTMZHBTBCTr4r1MZkJJt60ybz3REl92I0uKIynSMIUMXkUlMGAU8B5pRJ0533KImO0006EPpHUI",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "api.stripe.com",
        "Stripe-Version": "2020-08-27",
        "X-Stripe-User-Agent": json.dumps(
            {
                "os_version": "17.3.1",
                "model": "iPhone",
                "vendor_identifier": "521D44E8-0B56-460D-95A4-D74D91611B1F",
                "bindings_version": "23.18.2",
                "lang": "objective-c",
                "type": "iPhone16,2",
            }
        ),
    }

    try: 
        res2 = s.post(url2, data=payload2, headers=headers2, timeout=10)
    except Exception as e:
        thread_error(e)
        time.sleep(1)
        print(e, "retrying")
        return add_payment_info(s, token)

    if not res2.ok:
        thread_error(res2.status_code)
        return add_payment_info(s, token)

    payment_method_id = res2.json()["payment_method"]

    url3 = "https://api.resy.com/3/stripe/payment_method"

    payload3 = f"is_default=1&stripe_payment_method_id={payment_method_id}"
    headers3 = {
        "host": "api.resy.com",
        "content-type": "application/x-www-form-urlencoded; charset=utf-8",
        "accept": "*/*",
        "x-resy-auth-token": token,
        "accept-language": "en-US;q=1.0",
        "x-resy-universal-auth": token,
        "user-agent": RESY_UA,
        "authorization": 'ResyAPI api_key="AIcdK2rLXG6TYwJseSbmrBAy3RP81ocd"',
        "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
    }



    try:
        res3 = requests.post(
            url3, data=payload3, headers=headers3, proxies=proxies.get_proxy(), verify=False, timeout=10
        )    
    except Exception as e:
        thread_error(e)
        time.sleep(1)
        print(e, "retrying")
        return add_payment_info(s, token)

if __name__ == "__main__":
    thread_log("Resy Account Generator")
    thread_log("For use for ResMe research purposes only")
    print()
    thread_error("MAKE SURE YOU HAVE A VPN ON RIGHT NOW, THEN PRESS ENTER! ")
    print()
    input()
    num_accs = int(input("How many accounts to create per thread?: "))
    num_threads = int(input("Number of threads?: "))
    acc_type = input("Are these elite accounts? (y/n): ")

    if acc_type.lower() == "y":
        acc_type = "elite"
    else:
        acc_type = "normal"

    fake_domains = os.getenv("DOMAINS")
    for domain in fake_domains.split(","):
        domains.append(domain)

    print(domains)
    x = 0

    for i in range(num_threads):
        thread_id = f"Gen {x + 1}"

        if num_threads > 20:
            t = multiprocessing.Process(
                target=gen,
                name=thread_id,
                args=(
                    num_accs,
                    acc_type,
                ),
            )
            thread_log(f"Starting process {thread_id}")
        else:
            t = threading.Thread(
                target=gen,
                name=thread_id,
                args=(
                    num_accs,
                    acc_type,
                ),
            )
            thread_log(f"Starting thread {thread_id}")

        t.start()

        x += 1
