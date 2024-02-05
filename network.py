import requests
import urllib3
from utils import Utils
import os
import time
from proxies import Proxies

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

utils = Utils()
proxies = Proxies()


class Network:
    def __init__(self, proxy):
        # Config keys
        self.USER_AGENT = (
            "Resy/2.76.1 (com.resy.ResyApp; build:4977; iOS 17.3.0) Alamofire/5.8.0"
        )
        self.RESY_KEY = 'ResyAPI api_key="AIcdK2rLXG6TYwJseSbmrBAy3RP81ocd"'

        # Static Values
        self.MAX_ACC_RETRYS = 5
        self.MAX_INIT_BOOK_RETRYS = 5
        self.ERROR_DELAY = 0.5
        self.MAX_BOOK_RETRYS = 2
        self.ERROR_DELAY_CAL = 3
        self.ERROR_DELAY_LOGIN = 1

        self.session = requests.Session()
        self.proxies = proxy

    def get_session(self):
        return self.session

    def update_proxy(self, proxy):
        self.proxies = proxy

    def set_auth_token(self, auth_token):
        self.auth_token = auth_token

    def login(self, email, password):
        url = "https://api.resy.com/3/auth/password"

        payload = {"email": email, "password": password}

        headers = {
            "host": "api.resy.com",
            "connection": "keep-alive",
            "x-origin": "https://resy.com",
            "authorization": self.RESY_KEY,
            "user-agent": self.USER_AGENT,
            "content-type": "application/x-www-form-urlencoded",
            "accept": "application/json, text/plain, */*",
            "cache-control": "no-cache",
            "origin": "https://resy.com",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://resy.com/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
        }

        response = self.session.post(
            url,
            data=payload,
            headers=headers,
            proxies=proxies.get_proxy(),
            verify=False,
            timeout=10,
        )

        return response

    def account_reservations(self):
        url = f"https://api.resy.com/3/user/reservations?limit=1&offset=1&type=upcoming&book_on_behalf_of=false"

        headers = {
            "host": "api.resy.com",
            "connection": "keep-alive",
            "x-origin": "https://widgets.resy.com",
            "x-resy-auth-token": self.auth_token,
            "authorization": self.RESY_KEY,
            "user-agent": self.USER_AGENT,
            "x-resy-universal-auth": self.auth_token,
            "content-type": "application/json",
            "accept": "application/json, text/plain, */*",
            "cache-control": "no-cache",
            "origin": "https://widgets.resy.com",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://widgets.resy.com/",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
        }

        response = self.session.get(
            url, headers=headers, proxies=proxies.get_proxy(), verify=False
        )

        return response