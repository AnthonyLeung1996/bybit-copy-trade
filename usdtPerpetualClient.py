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

ETH_SYMBOL = 'ETHUSDT'
BTC_SYMBOL = 'BTCUSDT'

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

def getActivePositions(*, apiHost: str, apiKey: str, apiSecret: str):
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

def getSourceAccountPositions():
    return getActivePositions(
        apiHost = env.get_source_account_api_host(),
        apiKey = env.get_source_account_api_key(),
        apiSecret = env.get_source_account_api_secret()
    )

def getCopyAccountPositions():
    return getActivePositions(
        apiHost = env.get_copy_account_api_host(),
        apiKey = env.get_copy_account_api_key(),
        apiSecret = env.get_copy_account_api_secret()
    )

def makeOrder(quantity: str, symbol: Literal['BTCUSDT', 'ETHUSDT'], side: Literal['Buy', 'Sell']):
    endpoint = '/v5/order/create'
    url = env.get_copy_account_api_host() + endpoint
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
        env.get_copy_account_api_key(),
        env.get_copy_account_api_secret(),
        json.dumps(reqBody)
    )
    headers['Content-Type'] = 'application/json'
    response = requests.post(url=url, headers=headers, json=reqBody)
    data = response.json()
    return data

def setStopLossForSymbol(symbol: Literal['BTCUSDT', 'ETHUSDT'], position):
    positionIdx = position['positionIdx']
    markPrice = position['markPrice']
    positionValue = position['positionValue']
    endpoint = '/v5/position/trading-stop'
    url = env.get_source_account_api_host() + endpoint

    leverageRatio = Decimal(env.get_leverage_ratio())
    if leverageRatio.is_zero():
        return

    isReverse = leverageRatio < 0
    stopLossRate = Decimal(env.get_stop_loss_rate())
    if stopLossRate < 0:
        raise Exception('🔴 BYBIT_STOP_LOSS_PERCENT cannot be less than 0')

    reqBody = {
        "category": "linear",
        "symbol": symbol,
        "positionIdx": positionIdx
    }

    sign = Decimal("-1.0") if isReverse else Decimal("1.0")
    if positionIdx == 1: # long position
        sign *= Decimal("-1.0")
    
    stopLossPrice = Decimal(markPrice) + sign * Decimal(positionValue) * stopLossRate

    if isReverse:
        reqBody['takeProfit'] = "%.2f" % stopLossPrice
        reqBody['stopLoss'] = "0.00"
    else:
        reqBody['takeProfit'] = "0.00"
        reqBody['stopLoss'] = "%.2f" % stopLossPrice
        
    logger.info('[%s] Set stop loss: %.2f' % (symbol, stopLossPrice))

    headers = getAuthHeaders(
        env.get_source_account_api_key(),
        env.get_source_account_api_secret(),
        json.dumps(reqBody)
    )
    headers['Content-Type'] = 'application/json'
    response = requests.post(url=url, headers=headers, json=reqBody)
    data = response.json()
    return data

def syncCopyAccountToSourceAccountAndSetSL():
    sourcePositions = getSourceAccountPositions()
    copyPositions = getCopyAccountPositions()

    if not sourcePositions or sourcePositions['retCode'] != 0 :
        raise Exception('Cannot get position of source account')
    if not copyPositions or copyPositions['retCode'] != 0:
        raise Exception('Cannot get position of copy account')
    
    logger.info('')
    logger.info('============= Sync Start ============')
    
    btcSourcePosition = Decimal('0')
    ethSourcePosition = Decimal('0')
    btcCopyPosition = Decimal('0')
    ethCopyPosition = Decimal('0')
    leverageRatio = Decimal(env.get_leverage_ratio())

    logger.info('Leverage: {}'.format(leverageRatio))
    
    for position in sourcePositions['result']['list']:
        logger.info(position)
        # set stop loss
        response = setStopLossForSymbol(
            position['symbol'], 
            position
        )

        if response and 'retCode' in response:
            if response['retCode'] != 34040:
                logger.info('[%s] Stop loss not modified: %s' % (position['symbol']))
            elif response['retCode'] != 0:
                logger.info('🔴 [%s] Failed to set stop loss: %s' % (position['symbol'], str(response)))

        # record position size
        size = Decimal(position['size'])
        if position['symbol'] == BTC_SYMBOL:
            btcSourcePosition = size if position['side'] == 'Buy' else -size
        elif position['symbol'] == ETH_SYMBOL:
            ethSourcePosition = size if position['side'] == 'Buy' else -size

    logger.info('Current Source positions:')
    logger.info('> BTC: {}'.format(btcSourcePosition))
    logger.info('> ETH: {}'.format(ethSourcePosition))
    
    for position in copyPositions['result']['list']:
        size = Decimal(position['size'])
        if position['symbol'] == BTC_SYMBOL:
            btcCopyPosition = size if position['side'] == 'Buy' else -size
        elif position['symbol'] == ETH_SYMBOL:
            ethCopyPosition = size if position['side'] == 'Buy' else -size

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
            res = makeOrder(quantity=str(abs(btcOrderQty)), symbol=BTC_SYMBOL, side=side)
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
            res = makeOrder(quantity=str(abs(ethOrderQty)), symbol=ETH_SYMBOL, side=side)
            if 'retCode' in res and  res['retCode'] == 0:
                logger.info('🟢 ETH order submitted')
            else:
                logger.error('🔴 ETH order rejected: {}'.format(res))
        except Exception as e:
            logger.error('🔴 Error when submitting ETH order: {}'.format(e))
    
    if btcOrderQty.is_zero() and ethOrderQty.is_zero():
        logger.info('✅ Positions Already Up-to-date')

    logger.info('=========== Sync Complete ===========')