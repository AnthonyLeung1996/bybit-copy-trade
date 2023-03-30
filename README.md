# bybit-monitor

## Python version
Following setting works for me, other similar versions may also works:
```
Python 3.11.2
pip 22.3.1
```

## Install dependencies

Run following command:
```
pip3 install -r requirements.txt
```

try remove existing packages and reinstall if something go wrong:
```
pip3 uninstall -r requirements.txt -y
pip3 install -r requirements.txt
```


## Run application
Simply run in terminal:
```
python3 bybitMontior.py
python3 bybitMontior.py >> trades.log
```

Run using docker-compose:
```
docker-compose up --build --detach
```

## Environment variables vequired

This program require API key credentials of your ByBit account:

```bash
BYBIT_MONITOR_API_KEY="api key with read permission"
BYBIT_MONITOR_API_SECRET="secret of the api key mentioned above"
```

Step to create API key:
1. Log into your ByBit account (or subaccount) that you want to monitor 
2. Go https://www.bybit.com/app/user/api-management
3. Click "Create New Key" button
4. Select "System-generated API Keys"
5. Fill in the API key name you like
6. Select "Read-only" (recommended)
7. Either select "No IP restriction" or fill in the IP address if you know them.
8. Check "Derivatives API V3" > "Trade"