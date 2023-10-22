import os
from decimal import Decimal

def get_websocket_channel():
    return os.environ['BYBIT_WEBSOCKET_CHANNEL']

def get_source_account_api_key():
    return os.environ['BYBIT_SOURCE_ACCOUNT_API_KEY']

def get_source_account_api_secret():
    return os.environ['BYBIT_SOURCE_ACCOUNT_API_SECRET']

def get_source_account_api_host():
    return os.environ['BYBIT_SOURCE_ACCOUNT_API_HOST']

def get_copy_account_api_key():
    return os.environ['BYBIT_COPY_ACCOUNT_API_KEY']

def get_copy_account_api_secret():
    return os.environ['BYBIT_COPY_ACCOUNT_API_SECRET']

def get_copy_account_api_host():
    return os.environ['BYBIT_COPY_ACCOUNT_API_HOST']

def get_leverage_ratio():
    return os.environ['BYBIT_LEVERAGE_RATIO']

def get_stop_loss_rate():
    return os.environ['BYBIT_STOP_LOSS_RATE']

# ensure all variable exists
if any(filter(lambda x: x == None, [
    get_websocket_channel(),
    get_source_account_api_key(),
    get_source_account_api_secret(),
    get_source_account_api_host(),
    get_copy_account_api_key(),
    get_copy_account_api_secret(),
    get_copy_account_api_host(),
    get_leverage_ratio(),
    get_stop_loss_rate()
    ])):
    raise Exception("Please provide all the required environment variables.")

if Decimal(get_stop_loss_rate()) > 0.5:
    raise Exception('Stop loss rate too large')

if Decimal(get_stop_loss_rate()) < 0:
    raise Exception('Stop loss rate cannot be negative')