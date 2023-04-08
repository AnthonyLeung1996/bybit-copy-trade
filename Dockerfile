FROM python:3.9.16-bullseye

ENV BYBIT_SOURCE_ACCOUNT_API_KEY=${BYBIT_SOURCE_ACCOUNT_API_KEY}
ENV BYBIT_SOURCE_ACCOUNT_API_SECRET=${BYBIT_SOURCE_ACCOUNT_API_SECRET}
ENV BYBIT_COPY_ACCOUNT_API_KEY=${BYBIT_COPY_ACCOUNT_API_KEY}
ENV BYBIT_COPY_ACCOUNT_API_SECRET=${BYBIT_COPY_ACCOUNT_API_SECRET}
ENV BYBIT_SOURCE_ACCOUNT_API_HOST=${BYBIT_SOURCE_ACCOUNT_API_HOST}
ENV BYBIT_COPY_ACCOUNT_API_HOST=${BYBIT_COPY_ACCOUNT_API_HOST}

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "bybitCopyTrade.py"]