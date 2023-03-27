import websocket
import rel
import json
import hmac
import os   
import logging

logging.basicConfig(filename='monitor.log',
    filemode='a',
    format='[%(asctime)s.%(msecs)d][%(name)s][%(levelname)s]: %(message)s',
    datefmt='%H:%M:%S',
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
    logging.info(message)

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
    }))
    

if __name__ == "__main__":
#    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.bybit.com/v5/private",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    
    ws.run_forever(ping_interval=60, dispatcher=rel, reconnect=5) # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()