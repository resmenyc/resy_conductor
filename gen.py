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
proxiex = Proxies()
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

STRIPE_UA = "Resy/4977 CFNetwork/1492.0.1 Darwin/23.3.0"
STRIPE_P_UA = "stripe-ios/23.18.2; variant.legacy; PaymentSheet"

def gen(num_accs, acc_type):
    failure_cnt = 0
    
    try:
        cnt = 0
        for _ in range(num_accs):
            s = requests.Session()
            
            # Generate fake information
            first_name, last_name = gen_name()
            email = email_gen.gen()
            password = gen_password()
            
            
            
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)

def gen_name(self):    
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


if __name__ == "__main__":
    # Intro print
    print()
    utils.thread_log("Resy Account Generator")
    utils.thread_log("For use for ResMe research purposes only")
    print()
    utils.thread_error("!!! MAKE SURE YOU HAVE A VPN ENABLED !!!")
    print()
    print("*" * 40)
    print()

    # If were using arguments 1 = num accs, 2 = threads, 3 = acc type
    if len(sys.argv) > 1:
        num_accs = int(sys.argv[1])
        num_threads = int(sys.argv[2])
        acc_type = sys.argv[3]
    else:
        num_accs = int(input("How many accounts to create per thread?: "))
        num_threads = int(input("Number of threads?: "))
        acc_type = input("Are these elite accounts? (y/n): ")

    print()
    
    # TODO: change this to add more account types
    # Load in more data and set some conditions before we launch
    if acc_type.lower().replace(" ", "") == "y":
        acc_type = "elite"
    else:
        acc_type =  "normal"
    
    cnt = 0
    
    for _ in range(num_threads):
        thread_id = f"Gen {cnt + 1}"
        
        
        threading.Thread(
            target=gen,
            name=thread_id,
            args=(
                num_accs,
                acc_type,
            ),
        ).start()
        
        utils.thread_warn(f"Starting gen thread {thread_id}")
        time.sleep(0.5)
        cnt += 1
