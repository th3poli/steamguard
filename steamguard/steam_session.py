import os
import json
import time
import base64
import requests
from datetime import datetime, timezone

from .exceptions import *

USER_AGENT_MOBILE = 'Dalvik/2.1.0 (Linux; U; Android 9; Valve Steam App Version/3)'

class SteamSession:

    def __init__(self, account_name: str, password: str) -> None:

        self.account_name = account_name
        self._password = password

        self.steamid = None
        self.access_token = None
        self.refresh_token = None # INFO: If refresh_token is expired, I guess we've to login again?
        self.session_id = None

        self.__steamTimeDiff = 0
        self.__steamTimeAligned = False

        self.session = requests.Session()
        self.session.headers.update({ 'User-Agent': USER_AGENT_MOBILE })

        self.default_folder = '.th3poli-steamguard'

    def refresh_access_token(self):
        if not self.refresh_token: raise RefreshTokenEmpty('Refresh token is empty')
        if self.is_token_expired(self.refresh_token): raise RefreshTokenExpired('Refresh token expired')

        data = { 'steamid': self.steamid, 'refresh_token': self.refresh_token }

        res = self.session.post("https://api.steampowered.com/IAuthenticationService/GenerateAccessTokenForApp/v1", data=data)
        res = res.json().get('response')
        self.access_token = res.get('access_token', self.access_token)
        self.refresh_token = res.get('refresh_token', self.refresh_token)
        pre = self.steamid + '%7C%7C'
        self.session.cookies.set('steamLoginSecure', pre + self.access_token, domain='steamcommunity.com')
        self.session.cookies.set('steamLoginSecure', pre + self.access_token, domain='store.steampowered.com')
        self.session.cookies.set('steamRefresh_steam', pre + self.refresh_token, domain='login.steampowered.com')

    def is_token_expired(self, token: str): return datetime.now(timezone.utc).timestamp() > self.get_token_expire_timestamp(token) # TODO: Can't it be just int(time.time())

    def get_token_expire_timestamp(self, token: str):
        if not token: return 0

        token_components = token.split('.')
        base64_str = token_components[1].replace('-', '+').replace('_', '/')
        if len(base64_str) % 4 != 0: base64_str += '=' * (4 - len(base64_str) % 4)

        payload_bytes = base64.b64decode(base64_str)
        return json.loads(payload_bytes.decode('utf-8')).get('exp')

    def get_steam_time(self):
        if not self.__steamTimeAligned: self.align_time()
        return int(time.time() + self.__steamTimeDiff)

    def align_time(self):
        currentTime = int(time.time())

        params = { 'steamid': '0' }
        res = self.session.post('https://api.steampowered.com/ITwoFactorService/QueryTime/v0001', params=params).json()
        res = res.get('response')

        self.__steamTimeAligned = True
        self.__steamTimeDiff = int(int(res.get('server_time')) - currentTime)

    def export(self):
        return {
            'steamid': self.steamid,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'session_id': self.session_id,
            'account_name': self.account_name,
            'cookies': self.export_cookies_dict()
        }

    def export_cookies_dict(self):
        return [{ 'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path, 'secure': c.secure, 'expires': c.expires } for c in self.session.cookies]

    def export_cookies(self):
        return [c for c in self.session.cookies]

    def save_exported_data(self, data: dict, path: str):
        os.makedirs(self.default_folder, exist_ok=True)
        path = os.path.join(self.default_folder, path)
        with open(path, 'w', encoding='utf-8') as file: file.write(json.dumps(data))

    def load_exported_data(self, path: str, default = None):
        os.makedirs(self.default_folder, exist_ok=True)
        path = os.path.join(self.default_folder, path)
        if not os.path.isfile(path): return default
        with open(path, 'r', encoding='utf-8') as file: return json.loads(file.read())
