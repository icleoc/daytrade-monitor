from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Ativos monitorados (símbolo -> nome)
ASSETS = {
    "BTC/USD": "BTC-USD",
    "ETH/USD": "ETH-USD",
    "XAU/USD": "GC=F",
    "EUR/USD": "EURUSD=X"
}

def get_market_data():
    prices = {}
    for name, symbol in ASSETS.items():
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="15m")
        if not hist.empty:
            prices[name] = float(hist['Close'][-1])
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
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
