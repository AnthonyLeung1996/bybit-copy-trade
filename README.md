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
```bash
python3 bybitCopyTrade.py
python3 bybitCopyTrade.py >> trades.log
```

Run using docker-compose:
```bash
docker-compose up --no-deps --build --detach
```

Following the log:
```bash
docker-compose logs -f --tail 30
```

## Environment variables vequired

This program require API key credentials of your ByBit account:

Use `vim ~/.bash_profile` or `vim ~/.zshrc` to add following:
```bash
export BYBIT_WEBSOCKET_CHANNEL=wss://stream.bybit.com/v5/private
export BYBIT_SOURCE_ACCOUNT_API_KEY=dRSdK97OGxxxxxxxxx
export BYBIT_SOURCE_ACCOUNT_API_SECRET=fSkdrHyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export BYBIT_COPY_ACCOUNT_API_KEY=GUieV4pzasxxxxxxxx
export BYBIT_COPY_ACCOUNT_API_SECRET=F2enMITxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export BYBIT_SOURCE_ACCOUNT_API_HOST=https://api.bybit.com
export BYBIT_COPY_ACCOUNT_API_HOST=https://api-testnet.bybit.com
export BYBIT_LEVERAGE_RATIO=5
```

Apply the change to current terminal:
```bash
source ~/.bash_profile
or
source ~/.zshrc
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

## Position Mode

Note that the copy account need to use "One-Way Mode" setting for both ETHUSDT and BTCUSDT.

## Steps to change leverage

1. Change environment variable `BYBIT_LEVERAGE_RATIO` by `vim ~/.bash_profile`.
2. Apply the profile to terminal: `source ~/.bash_profile`.
3. Rebuild and restart the docker-compose: `docker-compose up --build --detach`
4. Done, the app will update the positions itself.
