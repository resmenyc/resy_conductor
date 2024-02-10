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
import threading
from termcolor import colored
import colorama
from database import Database
from aesCipher import AESCipher
from proxies import Proxies
import time
from wonderwords import RandomWord

colorama.init()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
database = Database()
proxies = Proxies()
aesCipher = AESCipher(os.getenv("ENCRYPTION_KEY"))
domains = []

RESY_UA = "Resy/2.76.1 (com.resy.ResyApp; build:4977; iOS 17.3.0) Alamofire/5.8.0"
STRIPE_UA = "Resy/4977 CFNetwork/1492.0.1 Darwin/23.3.0"
STRIPE_P_UA = "stripe-ios/23.18.0; variant.legacy; PaymentSheet"


def gen_email(first_name, last_name, fake_domain):
    fake = Faker()
    faker_email = fake.email()

    base_email_prefix = faker_email.split("@")[0]
    email = f"{first_name}{base_email_prefix}{randint(10, 999)}@{fake_domain}"

    return email


def gen_email_2(first_name, last_name, fake_domain):
    return f"{first_name}.{last_name}{randint(10, 999)}@{fake_domain}"


def gen_email_3(first_name, last_name, fake_domain):
    fake = Faker()
    faker_email = fake.email()

    base_email_prefix = faker_email.split("@")[0]
    email = f"{last_name}{base_email_prefix}@{fake_domain}"

    return email

def gen_email_4(first_name, last_name, fake_domain):
    return f"{first_name}{RandomWord().word()}{randint(10, 999)}@{fake_domain}".lower()

def gen_email_5(first_name, last_name, fake_domain):
    first_initial = first_name[:1]
    return f"{first_initial}{last_name}{randint(10, 999)}@{fake_domain}".lower()

def gen_email_6(first_name, last_name, fake_domain):
    last_initial = last_name[:1]
    return f"{first_name}{last_initial}{randint(10, 999)}@{fake_domain}".lower()

def gen_email_7(first_name, last_name, fake_domain):
    return gen_email_8(first_name, last_name, fake_domain)


def gen_email_8(first_name, last_name, fake_domain):
    return f"{RandomWord().word()}{last_name}{randint(10, 999)}@{fake_domain}".lower()

# TODO:add weights to each one
gen_email_methods = [gen_email, gen_email_2, gen_email_3, gen_email_4, gen_email_5, gen_email_6, gen_email_7, gen_email_8]

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

    return f"${password}"


def gen(num_accs, acc_type):
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

        token = create(s, first_name, last_name, email, password, phone_num)

        if token != None:
            try:
                add_payment_info(s, token)
                write_account_to_db(
                    email, password, first_name, last_name, phone_num, acc_type
                )
                x += 1
                print()
                thread_success(f"Generated Account {x}/{num_accs} [{email}]")
            except Exception as e:
                print(e)
                thread_error("Error adding payment info")

def gen_phone_num():
    fake = Faker()
    phone_num = fake.phone_number()
    if "x" in phone_num:
        phone_num = phone_num.split("x")[0]
    phone_num = phone_num.replace(".", "")
    phone_num = phone_num.replace("-", "")
    phone_num = phone_num.replace("(", "")
    phone_num = phone_num.replace(")", "")

    # replace the first three characters with 212
    phone_num = phone_num.replace(phone_num[0:3], "347", 1)

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
        "created_at": time.time(),
    }

    database.upload_account(account)


def write_account_to_file(email, password, first_name, last_name, phone_num):
    with open("accs.txt", "a+") as f:
        f.write(f"{email}|{password}|{first_name}|{last_name}|{phone_num}\n")


def create(s, first_name, last_name, email, password, phone_num, retry=False):
    url = "https://api.resy.com/2/user/registration"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": 'ResyAPI api_key="AIcdK2rLXG6TYwJseSbmrBAy3RP81ocd"',
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "Dnt": "1",
        "Origin": "https://resy.com",
        "Referer": "https://resy.com/",
        "User-Agent": RESY_UA,
        "X-Origin": "https://resy.com",
    }

    phone_num_prefix = ["347", "212", "917"]

    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "mobile_number": f"+1{phone_num.replace(phone_num[0:3], choice(phone_num_prefix), 1)}",
        "em_address": email,
        "policies_accept": 1,
        "marketing_opt_in": 0,
        "complete": 1,
        "device_type_id": 3,
        "device_token": str(uuid.uuid4()),
        "isNonUS": 0,
        "password": password,
    }

    res = s.post(url, headers=headers, data=payload, proxies=proxies.get_proxy(), verify=False)
    if res.status_code != 201:
        return None

    auth_token = res.json()["user"]["token"]

    return auth_token


def add_payment_info(s, token):
    url = "https://api.resy.com/3/stripe/setup_intent"

    headers = {
        "host": "api.resy.com",
        "accept": "*/*",
        "connection": "keep-alive",
        "x-resy-auth-token": token,
        "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        "x-resy-universal-auth": token,
        "user-agent": RESY_UA,
        "accept-language": "en-US;q=1.0",
        "authorization": 'ResyAPI api_key="AIcdK2rLXG6TYwJseSbmrBAy3RP81ocd"',
    }

    res = s.post(url, headers=headers, proxies=proxies.get_proxy(), verify=False)

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
        "host": "api.stripe.com",
        "content-type": "application/x-www-form-urlencoded",
        "accept-encoding": "gzip, deflate, br",
        "stripe-version": "2020-08-27",
        "user-agent": STRIPE_UA,
        "connection": "keep-alive",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "x-stripe-user-agent": '{"bindings_version":"23.18.0","model":"iPhone16,2","os_version":"17.3","vendor_identifier":"521D44E8-0B56-460D-95A4-D74D91611B1F","type":"iPhone16,2","lang":"objective-c"}',
        "authorization": "Bearer pk_live_51JdK5FIqT2RuI7QtpZsqeG1GTMZHBTBCTr4r1MZkJJt60ybz3REl92I0uKIynSMIUMXkUlMGAU8B5pRJ0533KImO0006EPpHUI",
    }

    res2 = s.post(url2, data=payload2, headers=headers2)

    payment_method_id = res2.json()["payment_method"]

    url3 = "https://api.resy.com/3/stripe/payment_method"

    payload3 = f"is_default=1&stripe_payment_method_id={payment_method_id}"
    headers3 = {
        "host": "api.resy.com",
        "content-type": "application/x-www-form-urlencoded; charset=utf-8",
        "accept": "*/*",
        "connection": "keep-alive",
        "x-resy-auth-token": token,
        "accept-language": "en-US;q=1.0",
        "x-resy-universal-auth": token,
        "user-agent": RESY_UA,
        "authorization": 'ResyAPI api_key="AIcdK2rLXG6TYwJseSbmrBAy3RP81ocd"',
        "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
    }

    res3 = requests.post(
        url3, data=payload3, headers=headers3, proxies=proxies.get_proxy(), verify=False
    )


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
