import os

SOURCE_ACCOUNT_API_KEY =  os.environ['BYBIT_SOURCE_ACCOUNT_API_KEY']
SOURCE_ACCOUNT_API_SECRET = os.environ['BYBIT_SOURCE_ACCOUNT_API_SECRET']
COPY_ACCOUNT_KEY =  os.environ['BYBIT_COPY_ACCOUNT_API_KEY']
COPY_ACCOUNT_SECRET = os.environ['BYBIT_COPY_ACCOUNT_API_SECRET']
SOURCE_ACCOUNT_API_HOST = os.environ['BYBIT_SOURCE_ACCOUNT_API_HOST']
COPY_ACCOUNT_API_HOST = os.environ['BYBIT_COPY_ACCOUNT_API_HOST']
LEVERAGE_RATIO = os.environ['BYBIT_LEVERAGE_RATIO']

if any(filter(lambda x: x == None, [
    SOURCE_ACCOUNT_API_KEY, 
    SOURCE_ACCOUNT_API_SECRET, 
    COPY_ACCOUNT_KEY,
    COPY_ACCOUNT_SECRET,
    SOURCE_ACCOUNT_API_HOST,
    COPY_ACCOUNT_API_HOST,
    LEVERAGE_RATIO
    ])):
    raise Exception("Please provide all the required environment variables.")