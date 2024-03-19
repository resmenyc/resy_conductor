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

if not os.getenv("ENCRYPTION_KEY"):
    utils.thread_error("No encryption key set")

aesCipher = AESCipher(os.getenv("ENCRYPTION_KEY"))

# GLOBALS
domains = []
STRIPE_UA = "Resy/4977 CFNetwork/1492.0.1 Darwin/23.3.0"
STRIPE_P_UA = "stripe-ios/23.18.2; variant.legacy; PaymentSheet"