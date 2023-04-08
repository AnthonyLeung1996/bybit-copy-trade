import time
import hmac
import hashlib
import urllib.parse
import requests
import json
from typing import Literal
from decimal import Decimal

import env

def getTimestampHeaderContent():
    return str(int(time.time() * 1000))

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

    print()
    print('============= Before Sync =============')
    print('[Source positions]', json.dumps(sourceOrders))
    print('[Copy positions]', json.dumps(copyOrders))
    print('=======================================')
    print()

    if not sourceOrders or sourceOrders['retCode'] != 0:
        raise Exception('Cannot get position of source account')
    if not copyOrders or copyOrders['retCode'] != 0:
        raise Exception('Cannot get position of copy account')
    
    btcOrderQty = Decimal('0')
    ethOrderQty = Decimal('0')
    for order in sourceOrders['result']['list']:
        size = Decimal(order['size'])
        if order['symbol'] == 'BTCUSDT':
            btcOrderQty = size if order['side'] == 'Buy' else -size
        elif order['symbol'] == 'ETHUSDT':
            ethOrderQty = size if order['side'] == 'Buy' else -size
    
    for order in copyOrders['result']['list']:
        size = Decimal(order['size'])
        if order['symbol'] == 'BTCUSDT':
            btcOrderQty -= size if order['side'] == 'Buy' else -size
        elif order['symbol'] == 'ETHUSDT':
            ethOrderQty -= size if order['side'] == 'Buy' else -size

    if not btcOrderQty.is_zero():
        side = 'Buy' if btcOrderQty > 0 else 'Sell'
        res = makeOrder(quantity=str(abs(btcOrderQty)), symbol='BTCUSDT', side=side)
        print('*** Syncing BTCUSDT position ({}):'.format(str(btcOrderQty)), json.dumps(res))
    if not ethOrderQty.is_zero():
        side = 'Buy' if ethOrderQty > 0 else 'Sell'
        res = makeOrder(quantity=str(abs(ethOrderQty)), symbol='ETHUSDT', side=side)
        print('*** Syncing ETHUSDT position ({}):'.format(str(ethOrderQty)), json.dumps(res))
    
    if btcOrderQty.is_zero() and ethOrderQty.is_zero():
        print()
        print('=======================================')
        print('|         Already up-to-date          |')
        print('=======================================')
        print()
    else:
        print()
        print('============ Sync Complete ============')
        print('[Source positions]', json.dumps(getSourceAccountActiveOrders()))
        print('[Copy positions]', json.dumps(getCopyAccountActiveOrders()))
        print('=======================================')
        print()