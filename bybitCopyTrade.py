import websocket
import rel
import json
import hmac
import time

import env
import usdtPerpetualClient
from logger import logger
from taskScheduler import TaskScheduler

def on_message(ws, message):
    messageDict = {}
    try:
        messageDict = json.loads(message)
    except Exception as e:
        logger.error('Error when parsing message')
        raise e
    
    if 'topic' not in messageDict or 'data' not in messageDict:
        return
    
    # logger.info(message)
    
    for data in messageDict['data']:
        isOrderRelevantAndFilled = 'category' in data and data['category'] == 'linear' and data['orderStatus'] == 'Filled'
        if not (isOrderRelevantAndFilled):
            continue

        logger.info('📩 {} {} {} (orderId: {})'.format(
            data['side'], data['symbol'][:3], data['qty'], data['orderId']
        ))
    
    usdtPerpetualClient.syncCopyAccountToSourceAccountAndSetSL()


def on_error(ws, error):
    logger.error(error)

def on_close(ws, close_status_code, close_msg):
    logger.info("### Websocket closed ###")
    logger.info("status code: {}, close msg: {}".format(close_status_code, close_msg))

def on_open(ws):
    expires = int(time.time() * 1000) + 2000
    signature = str(hmac.new(
        bytes(env.get_source_account_api_secret(), "utf-8"),
        bytes(f"GET/realtime{expires}", "utf-8"), digestmod="sha256"
    ).hexdigest())

    ws.send(
        json.dumps({
            "op": "auth",
            "args": [env.get_source_account_api_key(), expires, signature]
        })        
    )
    ws.send(
        json.dumps({
            "op": "subscribe",
            "args": ["order"]
        })
    )

    # update orders
    usdtPerpetualClient.syncCopyAccountToSourceAccountAndSetSL()

    # report balance
    balanceReporter = TaskScheduler(3600.0, usdtPerpetualClient.reportWalletBalance)
    balanceReporter.start()
    
class CustomWebSocketApp(websocket.WebSocketApp):
    def _send_ping(self):
        if self.stop_ping.wait(self.ping_interval):
            return
        while not self.stop_ping.wait(self.ping_interval):
            if self.sock:
                self.last_ping_tm = time.time()
                try:
                    self.sock.ping('')
                    self.sock.send(self.ping_payload)
                except Exception as ex:
                    websocket._logger.error("Failed to send ping: %s", ex)

if __name__ == "__main__":
    ping_body = json.dumps({
        "op": "ping"
    })
    ws = CustomWebSocketApp(env.get_websocket_channel(),
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever(ping_interval=60, ping_payload=ping_body, dispatcher=rel, reconnect=5) # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()