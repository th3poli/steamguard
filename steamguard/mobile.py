import rsa
from base64 import b64encode, b64decode

from .exceptions import *
from .steam_api_web import *
from .steam_session import SteamSession

import hmac
import base64
import struct
import hashlib

from .steam_api_mobile import *

class LoginConfirmType:
    none = 1
    email = 2
    mobile = 3

class SteamMobile(SteamSession):

    def __init__(self, account_name: str, password: str) -> None:

        self.__client_id = None
        self.__request_id = None
        self.__code_type = None

        self.device_id = generate_device_id()
        self.shared_secret = None
        self.serial_number = None
        self.revocation_code = None
        self.uri = None
        self.token_gid = None
        self.identity_secret = None
        self.secret_1 = None

        super().__init__(account_name=account_name, password=password)

    def load(self, data: dict):

        if not data: return

        self.steamid = data.get('steamid')
        self.access_token = data.get('access_token')
        self.refresh_token = data.get('refresh_token')
        self.session_id = data.get('session_id')

        for c in data.get('cookies', []): self.session.cookies.set(c['name'], c['value'], domain=c['domain'], path=c['path'], secure=c['secure'], expires=c['expires'])

    def load_mobile(self, data: dict):

        if not data: return

        self.device_id = data.get('device_id')

        self.shared_secret = data.get('shared_secret')
        self.serial_number = data.get('serial_number')
        self.revocation_code = data.get('revocation_code')
        self.uri = data.get('uri')
        self.token_gid = data.get('token_gid')
        self.identity_secret = data.get('identity_secret')
        self.secret_1 = data.get('secret_1')

    def login(self) -> LoginConfirmType:

        key, encryption_timestamp = getPasswordRSAPublicKey(self.session, self.account_name)

        encrypted_pass = b64encode(rsa.encrypt(self._password.encode(), key)).decode()

        res = beginAuthSessionViaCredentials(self.session, self.account_name, encrypted_pass, encryption_timestamp)

        if not res.get('steamid') or not res.get('client_id') or not res.get('request_id'): raise InvalidCredentials()

        self.steamid = res.get('steamid')
        self.__client_id = res.get('client_id')
        self.__request_id = res.get('request_id')

        # TODO: Check allowed_confirmations and make sure if it's without steamguard, email steamguard or mobile steamguard
        allowed_confirmations = res.get('allowed_confirmations') # Mobile -> 'allowed_confirmations': [{'confirmation_type': 3}], Email -> 2

        self.__code_type = int(allowed_confirmations[0].get('confirmation_type'))

        return self.__code_type #, allowed_confirmations[0].get('associated_message')

    def confirm_login(self, steam_guard_code: str = None):

        if self.__code_type != 1:
            updateAuthSessionWithSteamGuardCode(self.session, self.__client_id, self.steamid, steam_guard_code, self.__code_type) # INFO: We're not getting anything interesting from here

        res = pollAuthSessionStatus(self.session, self.__client_id, self.__request_id)

        if not res.get('account_name') or not res.get('access_token') or not res.get('refresh_token'): raise InvalidSteamGuardCode()

        self.access_token = res.get('access_token')
        self.refresh_token = res.get('refresh_token')

        finalizelogin(self.session, self.refresh_token)
        #self.session_id = self.session.cookies.get('sessionid', domain='steamcommunity.com') # TODO: Is session_id really necessary to be set? Can't we generate one?
    
    def get_steampowered(self): return self.session.get('https://store.steampowered.com/')
    def get_steamcommunity(self): return self.session.get('https://steamcommunity.com/')

    def add_phone_number(self, country_code: str, phone_number: str): # 48 - Poland :)

        res = phone_add_ajaxop(self.session, 'get_phone_number', f'+{country_code} {phone_number}')
        # => {'success': False, 'showResend': False, 'state': False, 'errorText': 'Your account already has a phone number attached to it.', 'token': '0'}
        # => {'success': True, 'showResend': False, 'state': 'email_verification', 'errorText': '', 'token': '0', 'phoneNumber': '+XX123456789'}

        if not res.get('success'):
            if res.get('errorText') == 'Your account already has a phone number attached to it.': raise AlreadyHasAPhoneNumber()
            raise UnknownException(res) # INFO: Well, I don't know every error :)

        return res

    def add_phone_number_email_verified(self):

        res = phone_add_ajaxop(self.session, 'email_verification')
        # => {'success': True, 'showResend': False, 'state': 'get_sms_code', 'errorText': '', 'token': '0', 'inputSize': '20', 'maxLength': '5'}
        #print('email verified ->', res)
        if res.get('state') == 'retry_email_verification': raise EmailNotVerified()
        if not res.get('success'): raise UnknownException(res)
        return res

    def add_phone_number_sms_code(self, code: str):

        res = phone_add_ajaxop(self.session, 'get_sms_code', code)
        # => {'success': True, 'showResend': False, 'state': 'done', 'errorText': '', 'token': '0', 'vac_policy': 0, 'tos_policy': 2, 'showDone': True, 'maxLength': '5'}
        # => {'success': False, 'showResend': False, 'state': False, 'errorText': 'Bad SMS code, please try again (CASM)', 'token': '0'}
        #print('get_sms_code ->', res)
        if res.get('errorText') == 'Bad SMS code, please try again (CASM)': raise InvalidSMSCode()
        if not res.get('success'): raise UnknownException(res)
        return res

    # WEB SESSION IS SIMULATED UP HERE
    # MOBILE SESSION IS SIMULATED DOWN HERE

    def deactivate_mobile_auth(self, steamguard_scheme: int = 1): # 1 - Return to email codes, 2 - Remove completly
        res = deactivateAuthenticator(self.session, self.revocation_code, self.access_token, steamguard_scheme)
        if not res.get('success'): raise UnknownException(res)
        return res

    def add_mobile_auth(self):
        res = addAuthenticator(self.session, self.access_token, self.steamid, self.device_id, str(self.get_steam_time()))
        status = res.get('status')

        # status codes TODO: Add more
        # 1 - ok
        # 2 - no phone number is on the account
        # 29 Already secured by Mobile Steam Guard

        if status == 29: raise AlreadyHasMobileSteamGuard()
        if not res.get('shared_secret') and not res.get('revocation_code'): raise UnknownException(res)

        self.shared_secret = res.get('shared_secret')
        self.serial_number = res.get('serial_number')
        self.revocation_code = res.get('revocation_code') # INFO: You can't lose this code!!! Save it every time!
        self.uri = res.get('uri')
        self.token_gid = res.get('token_gid')
        self.identity_secret = res.get('identity_secret')
        self.secret_1 = res.get('secret_1')

        return res

    def add_mobile_auth_confirm(self, sms_code: str):

        steam_guard_code = self.generate_steam_guard_code()

        res = finalizeAddAuthenticator(self.session, self.access_token, self.steamid, sms_code, steam_guard_code, str(self.get_steam_time()))

        if not res.get('success') or not res.get('status') == 2: raise UnknownException(res)

        if res.get('status') == 88: raise UnableToGenerateCorrectCodes()
        if res.get('status') == 89: raise InvalidSMSCode()

        return res

    def generate_steam_guard_code(self): return self.generate_steam_guard_code_for_time(self.get_steam_time())

    def generate_steam_guard_code_for_time(self, t: int):
        if not self.shared_secret: return None
        time_buffer = struct.pack('>Q', t // 30)
        time_hmac = hmac.new(base64.b64decode(self.shared_secret), time_buffer, digestmod=hashlib.sha1).digest()
        begin = ord(time_hmac[19:20]) & 0xF
        full_code = struct.unpack('>I', time_hmac[begin:begin + 4])[0] & 0x7FFFFFFF
        chars = '23456789BCDFGHJKMNPQRTVWXY'
        code = ''
        for _ in range(5):
            full_code, i = divmod(full_code, len(chars))
            code += chars[i]
        return code

    def export_mobile(self):
        return {
            'device_id': self.device_id,
            'shared_secret': self.shared_secret,
            'serial_number': self.serial_number,
            'revocation_code': self.revocation_code,
            'uri': self.uri,
            'token_gid': self.token_gid,
            'identity_secret': self.identity_secret,
            'secret_1': self.secret_1
        }

    # ====== #
    # TRADES #
    # ====== #

    def _send_confirmation(self, data_confid: str, nonce: str) -> dict:
        params = self._create_confirmation_params('allow')
        params['op'] = ('allow',)
        params['cid'] = data_confid
        params['ck'] = nonce
        headers = { 'X-Requested-With': 'XMLHttpRequest' }
        return self.session.get(f'https://steamcommunity.com/mobileconf/ajaxop', params=params, headers=headers).json()

    def _generate_confirmation_key(self, identity_secret: str, tag: str, timestamp: int) -> bytes:
        buffer = struct.pack('>Q', timestamp) + tag.encode('ascii')
        return b64encode(hmac.new(b64decode(identity_secret), buffer, digestmod=hashlib.sha1).digest())

    def get_trade_confirmations(self):
        params = self._create_confirmation_params('conf')
        headers = { 'X-Requested-With': 'com.valvesoftware.android.steam.community' }
        return self.session.get(f'https://steamcommunity.com/mobileconf/getlist', params=params, headers=headers)

    def _create_confirmation_params(self, tag_string: str):
        timestamp = int(time.time())
        confirmation_key = self._generate_confirmation_key(self.identity_secret, tag_string, timestamp)
        return {
            'p': self.device_id,
            'a': self.steamid,
            'k': confirmation_key,
            't': timestamp,
            'm': 'android',
            'tag': tag_string
        }

# TODO:
# Add tradeoffers confirmations
# Get inventory
# Get tradeable inventory