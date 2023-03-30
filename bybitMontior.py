import websocket
import rel
import json
import hmac
import os   
import logging
import time

logging.basicConfig(
    format='[%(name)s][%(levelname)s]: %(message)s',
    level=logging.DEBUG
)

api_key =  os.environ['BYBIT_MONITOR_API_KEY']
api_secret = os.environ['BYBIT_MONITOR_API_SECRET']
expires = 1681662381000

signature = str(hmac.new(
    bytes(api_secret, "utf-8"),
    bytes(f"GET/realtime{expires}", "utf-8"), digestmod="sha256"
).hexdigest())

def on_message(ws, message):
    if 'topic' in message:
        # trade message
        logging.info(message)
    else:
        logging.debug(message)

def on_error(ws, error):
    logging.error(error)

def on_close(ws, close_status_code, close_msg):
    logging.debug("### Websocket closed ###")
    logging.debug("status code: {}, close msg: {}".format(close_status_code, close_msg))

def on_open(ws):
    ws.send(
        json.dumps({
            "op": "auth",
            "args": [api_key, expires, signature]
        })        
    )
    ws.send(
        json.dumps({
            "op": "subscribe",
            "args": ["order"]
        })
    )
    
class CustomWebSocketApp(websocket.WebSocketApp):
    def _send_ping(self):
        if self.stop_ping.wait(self.ping_interval):
            return
        while not self.stop_ping.wait(self.ping_interval):
            if self.sock:
                self.last_ping_tm = time.time()
                try:
                    self.sock.send(self.ping_payload)
                except Exception as ex:
                    websocket._logging.debug("Failed to send ping: %s", ex)

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