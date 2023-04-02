FROM python:3.9.16-bullseye

ENV BYBIT_MONITOR_API_KEY=${BYBIT_MONITOR_API_KEY}

ENV BYBIT_MONITOR_API_SECRET=${BYBIT_MONITOR_API_SECRET}

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "bybitMontior.py"]