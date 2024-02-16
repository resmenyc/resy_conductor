import requests
import urllib3
from utils import Utils
from proxies import Proxies

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

utils = Utils()
proxies = Proxies()


class Network:
    def __init__(self, proxy):
        # Config keys
        self.USER_AGENT = (
            "Resy/2.77 (com.resy.ResyApp; build:5035; iOS 17.3.0) Alamofire/5.8.0"
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
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.RESY_KEY,
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Host": "api.resy.com",
            "User-Agent": self.USER_AGENT,
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
            "Accept": "*/*",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "Accept-Language": "en-US;q=1.0, fr-US;q=0.9",
            "Authorization": self.RESY_KEY,
            "Connection": "keep-alive",
            "Host": "api.resy.com",
            "User-Agent": self.USER_AGENT,
            "X-Resy-Auth-Token": self.auth_token,
            "X-Resy-Universal-Auth": self.auth_token,
            "cache-control": "no-cache",
        }

        response = self.session.get(
            url, headers=headers, proxies=proxies.get_proxy(), verify=False
        )

        return response
