from flask import Flask, render_template, jsonify
import requests
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# APIs públicas (sem necessidade de autenticação)
CRYPTO_URL = "https://min-api.cryptocompare.com/data/price"
FOREX_URL = "https://api.exchangerate.host/latest"
GOLD_URL = "https://min-api.cryptocompare.com/data/price"

def get_crypto_price(symbol, currency="USD"):
    try:
        res = requests.get(CRYPTO_URL, params={"fsym": symbol, "tsyms": currency}, timeout=10)
        res.raise_for_status()
        return res.json().get(currency)
    except Exception as e:
        print(f"Erro ao obter {symbol}: {e}")
        return None

def get_forex_price(base="EUR", target="USD"):
    try:
        res = requests.get(FOREX_URL, params={"base": base, "symbols": target}, timeout=10)
        res.raise_for_status()
        data = res.json()
        return data["rates"].get(target)
    except Exception as e:
        print(f"Erro ao obter {base}/{target}: {e}")
        return None

def get_gold_price(currency="USD"):
    try:
        res = requests.get(GOLD_URL, params={"fsym": "XAU", "tsyms": currency}, timeout=10)
        res.raise_for_status()
        return res.json().get(currency)
    except Exception as e:
        print(f"Erro ao obter ouro: {e}")
        return None

def get_market_data():
    prices = {
        "BTC/USD": get_crypto_price("BTC"),
        "ETH/USD": get_crypto_price("ETH"),
        "XAU/USD": get_gold_price(),
        "EUR/USD": get_forex_price()
    }
    prices = {k: v for k, v in prices.items() if v is not None}
    return prices

def calculate_vwap(prices):
    df = pd.DataFrame(prices.items(), columns=["symbol", "price"])
    df["volume"] = 1
    vwap = (df["price"] * df["volume"]).sum() / df["volume"].sum()
    return round(vwap, 2)

@app.route("/api/data")
def api_data():
    prices = get_market_data()
    vwap = calculate_vwap(prices)

    signals = {}
    for k, p in prices.items():
        signals[k] = "BUY" if p < vwap else "SELL"

    return jsonify({
        "prices": prices,
        "vwap": vwap,
        "signals": signals,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
