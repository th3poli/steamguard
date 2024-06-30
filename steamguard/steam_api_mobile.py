import time
import uuid
import requests

def generate_device_id(): return 'android:' + str(uuid.uuid4()) # "android:" + Guid.NewGuid().ToString()

def getSteamQueryTimeDifference(session: requests.Session):

    currentTime = int(time.time())

    params = { 'steamid': '0' }

    url = 'https://api.steampowered.com/ITwoFactorService/QueryTime/v0001'
    res = session.post(url, params=params).json()

    res = res.get('response')

    return int(int(res.get('server_time')) - currentTime)

def addAuthenticator(session: requests.Session, access_token: str, steamid: str, device_id: str, authenticator_time: str = None):

    data = {
        'steamid': steamid,
        'authenticator_type': '1',
        'device_identifier': device_id,
        #'authenticator_time': authenticator_time,
        'sms_phone_id': '1',
        'version': 2
    }

    params = { 'access_token': access_token }

    url = 'https://api.steampowered.com/ITwoFactorService/AddAuthenticator/v1'
    res = session.post(url, params=params, data=data)

    if res.status_code != 200: return None

    res = res.json()
    res = res.get('response')
    return res

def finalizeAddAuthenticator(session: requests.Session, access_token: str, steamid: str, code: str, steam_guard_code: str, authenticator_time: str):

    data = {
        'steamid': steamid,
        'activation_code': code,
        'authenticator_code': steam_guard_code,
        'authenticator_time': authenticator_time,
        #'validate_sms_code': '1'
    }

    params = { 'access_token': access_token }

    url = 'https://api.steampowered.com/ITwoFactorService/FinalizeAddAuthenticator/v1'
    res = session.post(url, params=params, data=data).json()

    res = res.get('response')
    return res

def deactivateAuthenticator(session: requests.Session, revocation_code: str, access_token: str, steamguard_scheme: int = 1): # 1 - Return to email codes, 2 - Remove completley

    data = {
        'revocation_code': revocation_code,
        'revocation_reason': '1',
        'steamguard_scheme': str(steamguard_scheme)
    }

    params = { 'access_token': access_token }

    url = "https://api.steampowered.com/ITwoFactorService/RemoveAuthenticator/v1"
    res = session.post(url, params=params, data=data).json()
    return res.get('response')

def fetchConfirmations(session: requests.Session, params: dict):
    res = session.get('https://steamcommunity.com/mobileconf/getlist', params=params).json()
    return res

def sendConfirmationAjaxop(session: requests.Session, params: dict):
    res = session.get('https://steamcommunity.com/mobileconf/ajaxop', params=params).json()
    return res