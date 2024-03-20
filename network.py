import requests
import urllib3
from utils import Utils
from proxies import Proxies
import uuid

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

utils = Utils()
proxies = Proxies()


class Network:
    def __init__(self, proxy):
        # Config keys
        self.USER_AGENT = (
            "Resy/2.78 (com.resy.ResyApp; build:5185; iOS 17.3.1) Alamofire/5.8.0"
        )
        self.RESY_KEY = 'ResyAPI api_key="AIcdK2rLXG6TYwJseSbmrBAy3RP81ocd"'
        self.RESY_KEY_NORM = 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"'

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
            "Origin": "https://resy.com",
            "Referer": "https://resy.com",
            "X-Origin": "https://resy.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        }

        response = self.session.post(
            url,
            data=payload,
            headers=headers,
            proxies=proxies.get_resi_proxy(),
            verify=False,
            timeout=15,
        )

        return response

    def create(self, first_name, last_name, email, password, phone_num):
        url = "https://api.resy.com/2/user/registration"
        
        headers = {
            "host": "api.resy.com",
            "content-type": "application/x-www-form-urlencoded; charset=utf-8",
            "accept": "*/*",
            "connection": "keep-alive",
            "user-agent": self.USER_AGENT,
            "accept-language": "en-US;q=1.0, fr-US;q=0.9",
            "authorization": self.RESY_KEY,
            "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
        }
        
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "mobile_number": f"+1{phone_num}",
            "em_address": email,
            "policies_accept": 1,
            "marketing_opt_in": 0,
            "complete": 1,
            "device_type_id": 2,
            "device_token": str(uuid.uuid4()).upper(),
            "isNonUS": 0,
            "password": password
        }
        
        response = self.session.post(
            url,
            headers=headers,
            data=payload,
            proxies=proxies.get_proxy(),
            verify=False,
            timeout=10
        )
        
        return response


    def account_reservations(self):
        url = f"https://api.resy.com/3/user/reservations?limit=1&offset=1&type=upcoming&book_on_behalf_of=false"

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "Accept-Language": "en-US;q=1.0, fr-US;q=0.9",
            "Authorization": self.RESY_KEY_NORM,
            "Connection": "keep-alive",
            "Host": "api.resy.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Resy-Auth-Token": self.auth_token,
            "X-Resy-Universal-Auth": self.auth_token,
            "cache-control": "no-cache",
        }

        response = self.session.get(
            url, headers=headers, proxies=proxies.get_proxy(), verify=False
        )

        return response