FROM python:3.11.2-bullseye
ENV BYBIT_MONITOR_API_KEY=${BYBIT_MONITOR_API_KEY}
ENV BYBIT_MONITOR_API_SECRET=${BYBIT_MONITOR_API_SECRET}
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .