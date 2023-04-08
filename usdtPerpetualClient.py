import time
import hmac
import hashlib
import urllib.parse
import requests
import json
from typing import Literal

import env

def getTimestampHeaderContent():
    return str(round(time.time() * 1000))

def getAuthHeaders(api_key, api_secret, payload):
    timestamp = getTimestampHeaderContent()
    recv_window = str(5000)
    param_str = timestamp + api_key + recv_window + payload
    hash = hmac.new(
        bytes(api_secret, "utf-8"), 
        param_str.encode("utf-8"),
        hashlib.sha256
    )
    signature = hash.hexdigest()
    return {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window,
    }

def getActiveOrders(*, apiHost: str, apiKey: str, apiSecret: str):
    endpoint = '/v5/position/list'
    url = apiHost + endpoint
    params = {
        'category': 'linear',
        'settleCoin': 'USDT'
    }
    queryStr = urllib.parse.urlencode(params)
    authHeader = getAuthHeaders(
        apiKey,
        apiSecret,
        queryStr
    )
    response = requests.get(url, params, headers=authHeader)
    data = response.json()
    return data

def getSourceAccountActiveOrders():
    return getActiveOrders(
        apiHost = env.SOURCE_ACCOUNT_API_HOST,
        apiKey = env.SOURCE_ACCOUNT_API_KEY,
        apiSecret = env.SOURCE_ACCOUNT_API_SECRET
    )

def getCopyAccountActiveOrders():
    return getActiveOrders(
        apiHost = env.COPY_ACCOUNT_API_HOST,
        apiKey = env.COPY_ACCOUNT_KEY,
        apiSecret = env.COPY_ACCOUNT_SECRET
    )

def makeOrder(quantity: str, symbol: Literal['BTCUSDT', 'ETHUSDT'], side: Literal['Buy', 'Sell']):
    endpoint = '/v5/order/create'
    url = env.COPY_ACCOUNT_API_HOST + endpoint
    reqBody = {
        "category": "linear",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": quantity,
        "timeInForce": "GTC"
    }
    headers = getAuthHeaders(
        env.COPY_ACCOUNT_KEY,
        env.COPY_ACCOUNT_SECRET,
        json.dumps(reqBody)
    )
    headers['Content-Type'] = 'application/json'
    response = requests.post(url=url, headers=headers, json=reqBody)
    data = response.json()
    return data

def syncCopyAccountToSourceAccount():
    sourceOrders = getSourceAccountActiveOrders()
    copyOrders = getCopyAccountActiveOrders()
    print(sourceOrders)
    print(copyOrders)

    if not sourceOrders or sourceOrders['retCode'] != 0:
        raise Exception('Cannot get position of source account')
    if not copyOrders or copyOrders['retCode'] != 0:
        raise Exception('Cannot get position of copy account')
    
    ethTargetBalance = 0.0
    btcTargetBalance = 0.0
    print(len(sourceOrders['result']['list']))
    print(len(copyOrders['result']['list']))
    

if __name__ == "__main__":
    # print(json.dumps(getSourceAccountActiveOrders(), indent=4))
    # print(json.dumps(getCopyAccountActiveOrders(), indent=4))
    # print(json.dumps(makeOrder(quantity="1.2", symbol='ETHUSDT', side='Buy'), indent=4))
    # print(json.dumps(makeOrder(quantity="0.052", symbol='BTCUSDT', side='Buy'), indent=4))
    syncCopyAccountToSourceAccount()