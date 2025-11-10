import os
import time
from flask import Flask, render_template, jsonify
import pandas as pd
from binance.client import Client
import requests

app = Flask(__name__)

# API Keys via variáveis de ambiente
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
BINANCE_API_SECRET = os.environ.get("BINANCE_API_SECRET")
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY")

# Inicializa cliente Binance
binance_client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

# Função para pegar dados de OHLC 15m da Binance
def get_binance_klines(symbol="BTCUSDT", interval="15m", limit=100):
    data = binance_client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close"] = df["close"].astype(float)
    return df

# Função para pegar EURUSD via Alpha Vantage (15min)
def get_eurusd():
    url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=15min&apikey={ALPHA_VANTAGE_KEY}&outputsize=compact"
    response = requests.get(url)
    data = response.json()
    try:
        last_key = list(data["Time Series FX (15min)"].keys())[0]
        close_price = float(data["Time Series FX (15min)"][last_key]["4. close"])
        return close_price
    except Exception:
        return None

@app.route("/api/data")
def get_data():
    try:
        btc = get_binance_klines("BTCUSDT").iloc[-1]["close"]
    except Exception:
        btc = None
    try:
        eth = get_binance_klines("ETHUSDT").iloc[-1]["close"]
    except Exception:
        eth = None
    try:
        xau = get_binance_klines("XAUUSDT").iloc[-1]["close"]
    except Exception:
        xau = None
    eurusd = get_eurusd()
    
    return jsonify({
        "BTCUSDT": btc,
        "ETHUSDT": eth,
        "XAUUSDT": xau,
        "EURUSD": eurusd
    })

@app.route("/")
def index():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
