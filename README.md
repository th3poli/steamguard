# Steamguard

**Steamguard** is a simple python module to add a phone number to your steam account and enable mobile auth. Also generate steam guard codes.

```
## Installing Steamguard

Steamguard is available on PyPI:

```console
$ python -m pip install steamguard
```


## Examples

1. Add phone number and mobile steam guard

```python
from steamguard import *

mobile = SteamMobile('<steam login>', '<steam password>')

mobile.get_steampowered()
mobile.get_steamcommunity()

code_type = mobile.login()

if code_type == LoginConfirmType.email:
    email_code = input('Enter Steam Guard Code Email > ')
    mobile.confirm_login(email_code)

elif code_type == LoginConfirmType.mobile:
    mobile_code = mobile.generate_steam_guard_code() or input('Enter Steam Guard Code Mobile > ')
    mobile.confirm_login(mobile_code)

data = mobile.export()
save_exported_data(data, f'{mobile.account_name}_cookies.json')

mobile.add_phone_number('12', '123456789')

input('I clicked the link sent to my email > ')
mobile.add_phone_number_email_verified()

sms_code = input('SMS Code > ')
mobile.add_phone_number_sms_code(sms_code)

mobile.add_mobile_auth()

# SAVE data_mobile! If you lose it, you'll lose access to your account!
data_mobile = mobile.export_mobile()
save_exported_data(data_mobile, f'{mobile.account_name}_mobile.json')

sms_code_confirm = input('SMS Code Confirm > ')
mobile.add_mobile_auth_confirm(sms_code_confirm)
```

2. Load <account_name>_mobile.json and generate steam guard code

```python
from steamguard import *

mobile = SteamMobile('<steam login>', '')

mobile_data = load_exported_data(f'{mobile.account_name}_mobile.json')

mobile.load_mobile(mobile_data)

guard_code = mobile.generate_steam_guard_code()
print(guard_code)
```

:)