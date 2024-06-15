import rsa
import requests

def getPasswordRSAPublicKey(session: requests.Session, account_name: str):
    url = 'https://api.steampowered.com/IAuthenticationService/GetPasswordRSAPublicKey/v1'
    res = session.get(url, params={ 'account_name': account_name }).json()
    res = res.get('response')
    public_key = rsa.PublicKey(int(res['publickey_mod'], 16), int(res['publickey_exp'], 16))
    return public_key, int(res['timestamp'])

def beginAuthSessionViaCredentials(session: requests.Session, account_name: str, encrypted_password: str, encryption_timestamp: int):

    params = {
        'account_name': account_name,
        'encrypted_password': encrypted_password,
        'encryption_timestamp': encryption_timestamp,
        'persistence': '1',
        #'device_friendly_name': '',
        #'remember_login': 'true',
        #'platform_type': '',
        #'guard_data': '',
        #'language': '',
        #'device_details': session.headers.get('User-Agent')
    }

    url = 'https://api.steampowered.com/IAuthenticationService/BeginAuthSessionViaCredentials/v1'
    res = session.post(url, params=params).json()
    res = res.get('response')
    return res

    client_id = res.get('client_id')
    request_id = res.get('request_id')
    allowed_confirmations = res.get('allowed_confirmations')
    steamid = res.get('steamid')

    if allowed_confirmations and steamid:

        print('steamid ->', steamid)
        print('allowed confirmations ->', allowed_confirmations)
        
        for allowed_conf in allowed_confirmations:
            confirmation_type = allowed_conf.get('confirmation_type')
            associated_message = allowed_conf.get('associated_message')
            if confirmation_type == 2: # email guard
                print('Get steam guard from ->', associated_message)

    return client_id, request_id, steamid

def updateAuthSessionWithSteamGuardCode(session: requests.Session, client_id: str, steamid: str, code: str, code_type: str = '2'):

    params = {
        'client_id': client_id,
        'steamid': steamid,
        'code': code,
        'code_type': code_type
    }

    url = 'https://api.steampowered.com/IAuthenticationService/UpdateAuthSessionWithSteamGuardCode/v1'
    res = session.post(url, params=params)
    return res

def pollAuthSessionStatus(session: requests.Session, client_id: str, request_id: str) -> dict:

    params = {
        'client_id': client_id,
        'request_id': request_id
    }

    url = 'https://api.steampowered.com/IAuthenticationService/PollAuthSessionStatus/v1'
    res = session.post(url, params=params).json()
    return res.get('response')

def finalizelogin(session: requests.Session, refresh_token: str):

    params = {
        'nonce': refresh_token,
        'sessionid': session.cookies.get(name='sessionid', domain='steamcommunity.com'),
        'redir': 'https://steamcommunity.com/login/home/?goto='
    }

    url = 'https://login.steampowered.com/jwt/finalizelogin'
    res = session.post(url, data=params)

    res = res.json()

    steamID = res.get('steamID')
    transfer_info = res.get('transfer_info')

    for transfer in transfer_info:
        transfer_url = transfer.get('url')

        if not transfer_url in ['https://store.steampowered.com/login/settoken', 'https://steamcommunity.com/login/settoken']: continue

        transfer_params = transfer.get('params')
        transfer_params['steamID'] = steamID

        session.post(transfer_url, params=transfer_params)

    return res

'''
get_phone_number -> {
    "success": true,
    "showResend": false,
    "state": "email_verification",
    "errorText": "",
    "token": "0",
    "phoneNumber": "+XX123456789"
}
'''

def phone_add_ajaxop(session: requests.Session, op: str = 'get_phone_number' or 'email_verification' or 'get_sms_code', input_: str = ''):

    data = {
        'op': op,
        'input': input_,
        'sessionID': session.cookies.get(name='sessionid', domain='store.steampowered.com'),
        'confirmed': '1',
        'checkfortos': '1',
        'bisediting': '0',
        'token': '0'
    }

    url = 'https://store.steampowered.com/phone/add_ajaxop'
    res = session.post(url, data=data)
    return res.json()

from bs4 import BeautifulSoup

def get_tradelink(session: requests.Session):
    res = session.get('https://steamcommunity.com/my/tradeoffers/privacy')
    soup = BeautifulSoup(res.text, 'html.parser')
    element = soup.find(id='trade_offer_access_url')
    tradelink = element.get('value')
    return tradelink

def get_inventory(session: requests.Session, steamid: str):
    res = session.get(f"https://steamcommunity.com/inventory/{steamid}/730/2?l=polish&count=2000")
    return res

def get_tradeable_inventory(session: requests.Session, steamid: str):

    inventory = get_inventory(session, steamid).json()

    if not inventory: return []
    if inventory['total_inventory_count'] == 0: return []

    assets = inventory['assets']
    descriptions = inventory['descriptions']

    ready_assets = []
    for asset in assets:
        classid = asset['classid']
        assetid = asset['assetid']

        for desc in descriptions:
            if desc['classid'] == classid and desc['tradable']:
                ready_assets.append({ "tradeable": desc['tradable'], "assetid": assetid, 'tradeoffer_asset': { "appid":730,"contextid":"2","amount":1,"assetid": assetid } })
                break

    return ready_assets

def get_tradeoffer_details(session: requests.Session):
    
    res = session.get('')
