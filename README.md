# bybit-monitor

## Install dependencies

Run following command:
```
pip install -r requirements.txt
```

try remove existing packages and reinstall if something go wrong:
```
pip uninstall --yes websocket-client
pip uninstall --yes rel
pip install -r requirements.txt
```


## Run application

```
python bybitMontior.py
```

or 

```
python bybitMontior.py > trades.log
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
