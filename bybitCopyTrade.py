import websocket
import rel
import json
import hmac
import logging
import time
from decimal import Decimal
from datetime import datetime
from pytz import timezone

import env
import usdtPerpetualClient

def timetz(*args):
    return datetime.now(tz).timetuple()

tz = timezone('Asia/Tokyo')

logging.Formatter.converter = timetz

logging.basicConfig(
    format='[%(asctime)s][%(name)s][%(levelname)s]: %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
expires = 1681662381000

signature = str(hmac.new(
    bytes(env.SOURCE_ACCOUNT_API_SECRET, "utf-8"),
    bytes(f"GET/realtime{expires}", "utf-8"), digestmod="sha256"
).hexdigest())

def on_message(ws, message):
    messageDict = {}
    try:
        messageDict = json.loads(message)
    except Exception as e:
        logging.error('Error when parsing message')
        raise e
    
    if 'topic' not in messageDict or 'data' not in messageDict:
        return
    
    for data in messageDict['data']:
        isOrderRelevantAndFilled = 'category' in data and data['category'] == 'linear' and data['orderStatus'] == 'Filled'
        if not (isOrderRelevantAndFilled):
            continue

        logging.info('📩 {} {} {} (orderId: {})'.format(
            data['side'], data['symbol'][:3], data['qty'], data['orderId']
        ))
    
    usdtPerpetualClient.syncCopyAccountToSourceAccount()


def on_error(ws, error):
    logging.error(error)

def on_close(ws, close_status_code, close_msg):
    logging.info("### Websocket closed ###")
    logging.info("status code: {}, close msg: {}".format(close_status_code, close_msg))

def on_open(ws):
    ws.send(
        json.dumps({
            "op": "auth",
            "args": [env.SOURCE_ACCOUNT_API_KEY, expires, signature]
        })        
    )
    ws.send(
        json.dumps({
            "op": "subscribe",
            "args": ["order"]
        })
    )
    usdtPerpetualClient.syncCopyAccountToSourceAccount()
    
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
                    websocket._logging.error("Failed to send ping: %s", ex)

if __name__ == "__main__":
    ping_body = json.dumps({
        "op": "ping"
    })
    ws = CustomWebSocketApp("wss://stream.bybit.com/v5/private",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever(ping_interval=60, ping_payload=ping_body, dispatcher=rel, reconnect=5) # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()