# bybit-copy-trade

## Python version
Following setting works for me, other similar versions may also works:
```
Python 3.11.2
pip 22.3.1
```

## Install dependencies (for running in terminal)

Run following command:
```
pip3 install -r requirements.txt
```

try remove existing packages and reinstall if something go wrong:
```
pip3 uninstall -r requirements.txt -y
pip3 install -r requirements.txt
```

## Install dependencies (for running in Docker)

We use docker and docker-compose, so install it yourself.

## Run application
Simply run in terminal:
```
python3 bybitCopyTrade.py
python3 bybitCopyTrade.py >> trades.log
```

Run using docker-compose:
```
docker-compose up --build --detach
docker-compose logs -f -t
```

## Environment variables vequired

This program require API key credentials of your ByBit account:

```bash
BYBIT_SOURCE_ACCOUNT_API_KEY (Read-only)
BYBIT_SOURCE_ACCOUNT_API_SECRET (Read-only)
BYBIT_COPY_ACCOUNT_API_KEY (Read-Write)
BYBIT_COPY_ACCOUNT_API_SECRET (Read-Write)
BYBIT_SOURCE_ACCOUNT_API_HOST
BYBIT_COPY_ACCOUNT_API_HOST
```

- Source account means the account which you want to read the trading activities from, and copy account is the account will mimic the trades of source account.
- API host should be either <https://api-testnet.bybit.com> (Testnet) or <https://api.bybit.com> (Mainnet).

Step to create API key:

1. Log into your ByBit account (or subaccount) that you want to monitor.
2. Go <https://www.bybit.com/app/user/api-management>
3. Click "Create New Key" button
4. Select "System-generated API Keys"
5. Fill in the API key name you like
6. Select "Read-only" or "Read-Write"
7. Either select "No IP restriction" or fill in the IP address if you know them.
8. Check "Derivatives API V3" > "Trade"
