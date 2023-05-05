import time
import hmac
import hashlib
import urllib.parse
import requests
import json
from typing import Literal
from decimal import Decimal

from logger import logger
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
        "timeInForce": "GTC",
        "positionIdx": 0
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

    if not sourceOrders or sourceOrders['retCode'] != 0:
        raise Exception('Cannot get position of source account')
    if not copyOrders or copyOrders['retCode'] != 0:
        raise Exception('Cannot get position of copy account')
    
    logger.info('')
    logger.info('============= Sync Start ============')
    
    btcSourcePosition = Decimal('0')
    ethSourcePosition = Decimal('0')
    btcCopyPosition = Decimal('0')
    ethCopyPosition = Decimal('0')
    leverageRatio = Decimal(env.LEVERAGE_RATIO)

    logger.info('Leverage: {}'.format(leverageRatio))
    
    for order in sourceOrders['result']['list']:
        size = Decimal(order['size'])
        if order['symbol'] == 'BTCUSDT':
            btcSourcePosition = size if order['side'] == 'Buy' else -size
        elif order['symbol'] == 'ETHUSDT':
            ethSourcePosition = size if order['side'] == 'Buy' else -size
    logger.info('Current Source positions:')
    logger.info('> BTC: {}'.format(btcSourcePosition))
    logger.info('> ETH: {}'.format(ethSourcePosition))
    
    for order in copyOrders['result']['list']:
        size = Decimal(order['size'])
        if order['symbol'] == 'BTCUSDT':
            btcCopyPosition = size if order['side'] == 'Buy' else -size
        elif order['symbol'] == 'ETHUSDT':
            ethCopyPosition = size if order['side'] == 'Buy' else -size

    logger.info('Current Copy positions:')
    logger.info('> BTC: {}'.format(btcCopyPosition))
    logger.info('> ETH: {}'.format(ethCopyPosition))

    btcWantedPosition = btcSourcePosition * leverageRatio
    ethWantedPosition = ethSourcePosition * leverageRatio
    logger.info('Wanted Copy positions:')
    logger.info('> BTC: {}'.format(btcWantedPosition))
    logger.info('> ETH: {}'.format(ethWantedPosition))

    btcOrderQty = btcWantedPosition - btcCopyPosition
    ethOrderQty = ethWantedPosition - ethCopyPosition

    if not btcOrderQty.is_zero():
        side = 'Buy' if btcOrderQty > 0.0 else 'Sell'
        logger.info('⌛ Submitting BTC order ({}) ...'.format(btcOrderQty))
        try:
            res = makeOrder(quantity=str(abs(btcOrderQty)), symbol='BTCUSDT', side=side)
            if 'retCode' in res and res['retCode'] == 0:
                logger.info('🟢 BTC order submitted')
            else:
                logger.error('🔴 BTC order rejected: {}'.format(res))
        except Exception as e:
            logger.error('🔴 Error when submitting BTC order: {}'.format(e))
    
    if not ethOrderQty.is_zero():
        side = 'Buy' if ethOrderQty > 0.0 else 'Sell'
        logger.info('⌛ Submitting ETH order ({}) ...'.format(ethOrderQty))
        try:
            res = makeOrder(quantity=str(abs(ethOrderQty)), symbol='ETHUSDT', side=side)
            if 'retCode' in res and  res['retCode'] == 0:
                logger.info('🟢 ETH order submitted')
            else:
                logger.error('🔴 ETH order rejected: {}'.format(res))
        except Exception as e:
            logger.error('🔴 Error when submitting ETH order: {}'.format(e))
    
    if btcOrderQty.is_zero() and ethOrderQty.is_zero():
        logger.info('✅ Positions Already Up-to-date')

    logger.info('============ Sync Complete ============')