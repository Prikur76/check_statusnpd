import os
from environs import Env


env = Env()
env.read_env()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = \
    os.path.join(BASE_DIR, env.str('CREDENTIALS_FILE_NAME'))

ELEMENT_PARAMS = {
    'login': env.str('USERNAME'),
    'password': env.str('PASSWORD')
}

ELEMENT_URLS = {
    'base_url': env.str('BASE_URL'),
    'drivers': '/Driver/v1/Get'
}

GOOGLE_SHEETS_PARAMS = {
    'spreadsheet_id': env.str('SPREADSHEET_ID'),
    'range_name': env.str('RANGE_NAME')
}

# https://npd.nalog.ru/check-status/
STATUSNPD_ENDPOINT_URL = "https://statusnpd.nalog.ru:443/api/v1/tracker/taxpayer_status"
