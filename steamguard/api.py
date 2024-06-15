import os
import json

USER_AGENT_MOBILE = 'Dalvik/2.1.0 (Linux; U; Android 9; Valve Steam App Version/3)'
#USER_AGENT_WEB = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

DEFUALT_FOLDER = '.th3poli-steamguard'

def __make_folder():
    if not os.path.exists(DEFUALT_FOLDER): os.makedirs(DEFUALT_FOLDER)

def save_exported_data(data: dict, path: str):
    __make_folder()
    path = os.path.join(DEFUALT_FOLDER, path)
    with open(path, 'w', encoding='utf-8') as file: file.write(json.dumps(data))

def load_exported_data(path: str, default = None):
    __make_folder()
    path = os.path.join(DEFUALT_FOLDER, path)
    if not os.path.isfile(path): return default
    with open(path, 'r', encoding='utf-8') as file: return json.loads(file.read())
