# Steamguard

**Steamguard** is a simple python module to add a phone number to your steam account and enable mobile auth. Also generate steam guard codes.

## Installing Steamguard

Steamguard is available on PyPI:

```console
$ python -m pip install steamguard
```

Below you have Examples and also Tricks & Tips (tradeoffers confirmations, fetching inventory and more)

## Examples

1. Add phone number and mobile steam guard

```python
from steamguard import SteamMobile, LoginConfirmType

mobile = SteamMobile('<steam login>', '<steam password>')

mobile.get_steampowered()
mobile.get_steamcommunity()

code_type = mobile.login()

if code_type == LoginConfirmType.none:
    mobile.confirm_login()

elif code_type == LoginConfirmType.email:
    email_code = input('Enter Steam Guard Code Email > ')
    mobile.confirm_login(email_code)

elif code_type == LoginConfirmType.mobile:
    mobile_code = mobile.generate_steam_guard_code() or input('Enter Steam Guard Code Mobile > ')
    mobile.confirm_login(mobile_code)

data = mobile.export()
mobile.save_exported_data(data, f'{mobile.account_name}_cookies.json')

mobile.add_phone_number('12', '123456789')

input('I clicked the link sent to my email > ')
mobile.add_phone_number_email_verified()

sms_code = input('SMS Code > ')
mobile.add_phone_number_sms_code(sms_code)

mobile.add_mobile_auth()

# SAVE data_mobile! If you lose it, you'll lose access to your account!
data_mobile = mobile.export_mobile()
mobile.save_exported_data(data_mobile, f'{mobile.account_name}_mobile.json')

sms_code_confirm = input('SMS Code Confirm > ')
mobile.add_mobile_auth_confirm(sms_code_confirm)
```

2. Add mobile steam guard without phone number

```python
from steamguard import SteamMobile, LoginConfirmType

mobile = SteamMobile('<steam login>', '<steam password>')

mobile.get_steampowered()
mobile.get_steamcommunity()

code_type = mobile.login()

if code_type == LoginConfirmType.none:
    mobile.confirm_login()

elif code_type == LoginConfirmType.email:
    email_code = input('Enter Steam Guard Code Email > ')
    mobile.confirm_login(email_code)

elif code_type == LoginConfirmType.mobile:
    mobile_code = mobile.generate_steam_guard_code() or input('Enter Steam Guard Code Mobile > ')
    mobile.confirm_login(mobile_code)

data = mobile.export()
mobile.save_exported_data(data, f'{mobile.account_name}_cookies.json')

mobile.add_mobile_auth()

# SAVE data_mobile! If you lose it, you'll lose access to your account!
data_mobile = mobile.export_mobile()
mobile.save_exported_data(data_mobile, f'{mobile.account_name}_mobile.json')

email_code_confirm = input('Email Code Confirm > ')
mobile.add_mobile_auth_confirm(email_code_confirm)
```

3. Load <account_name>_mobile.json and generate steam guard code

```python
from steamguard import SteamMobile

mobile = SteamMobile('<steam login>', '')

mobile_data = mobile.load_exported_data(f'{mobile.account_name}_mobile.json')
mobile.load_mobile(mobile_data)

guard_code = mobile.generate_steam_guard_code()
print(guard_code)
```

## Tricks & Tips

You can change the default path for steamguard files
```python
from steamguard import SteamMobile

mobile = SteamMobile('<steam login>', '<steam password>')

mobile.default_folder = '<MY_FOLDER_PATH>'
```

I want to load previous session saved to <account_name>_cookies.json
```python
from steamguard import SteamMobile

mobile = SteamMobile('<steam login>', '<steam password>')

data = mobile.load_exported_data(f'{mobile.account_name}_cookies.json')
mobile.load(data)

mobile_data = mobile.load_exported_data(f'{mobile.account_name}_mobile.json')
mobile.load_mobile(mobile_data)

mobile.refresh_access_token()
```

I want to fetch my inventory
```python
import steamguard
from steamguard import SteamMobile

mobile = SteamMobile('<steam login>', '<steam password>')

data = mobile.load_exported_data(f'{mobile.account_name}_cookies.json')
mobile.load(data)

mobile.refresh_access_token()

res = steamguard.get_inventory(mobile.session, mobile.steamid)
print(res.json())

# SOMEONE ELSE INVENTORY
res2 = steamguard.get_inventory(mobile.session, '<steamid>')
print(res2.json())
```

I want to get my trade link
```python
import steamguard
from steamguard import SteamMobile

mobile = SteamMobile('<steam login>', '<steam password>')

data = mobile.load_exported_data(f'{mobile.account_name}_cookies.json')
mobile.load(data)

mobile.refresh_access_token()

tradelink = steamguard.get_tradelink(mobile.session)
print('My tradelink is:', tradelink)
```

I want to send a trade offer (this example will send ALL TRADEABLE ITEMS)
```python
import steamguard
from steamguard import SteamMobile

mobile = SteamMobile('<steam login>', '<steam password>')

data = mobile.load_exported_data(f'{mobile.account_name}_cookies.json')
mobile.load(data)

mobile.refresh_access_token()

tradeable_items = steamguard.get_tradeable_inventory(mobile.session, mobile.steamid)

if not len(tradeable_items):
    print('No items to send :(')
else:
    res = steamguard.send_tradeoffer(mobile.session, partner_steamid, tradeoffer_token, tradeable_items, 'My custom message :)') # I don't know if tradeoffer_token is necessary if we're friends
    if res.status_code != 200:
        print(f'Error -> ({res.status_code}) {res.text}')
    else:
        d = res.json()
        tradeofferid = d.get('tradeofferid')

        confirm_type = 'Mobile Confirm' if d.get('needs_mobile_confirmation') else 'Email Confirm'
        print(f'Tradeoffer {tradeofferid} sent, now confirm it -> {confirm_type}')
```

Fetch and confirm pending tradeoffers
```python
from steamguard import SteamMobile

mobile = SteamMobile('<steam login>', '<steam password>')

data = mobile.load_exported_data(f'{mobile.account_name}_cookies.json')
mobile.load(data)

mobile_data = mobile.load_exported_data(f'{mobile.account_name}_mobile.json')
mobile.load_mobile(mobile_data)

mobile.refresh_access_token()

res = mobile.get_trade_confirmations()
data = res.json()
if not data.get('success'):
    print(mobile.account_name, res, data)
else:
    for d in data.get('conf'):
        headline = d.get('headline')
        offerid = d.get('id')
        nonce = d.get('nonce')
        print(f'Trading with: {headline} ({offerid})')
        res2 = mobile._send_confirmation(offerid, nonce)
        if res2.get('success'): print(f'Tradeoffer sent! ({headline})')
        else: print('Failed to confirm tradeoffer', res2)
```

:)