import websocket
import _thread
import time
import rel
import json
import hmac

api_key = "RGhYXtjVCByTGtG1WE"
api_secret = "Xp4PBajAuDtku7yVSdOdc4mTdFXma0SkV9Iu"
expires = 1681662381000

signature = str(hmac.new(
    bytes(api_secret, "utf-8"),
    bytes(f"GET/realtime{expires}", "utf-8"), digestmod="sha256"
).hexdigest())

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")
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
    
    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()