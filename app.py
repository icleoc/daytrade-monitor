from flask import Flask, jsonify, render_template
import requests
import os
import threading
import time

app = Flask(__name__)

# API Keys
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")

# Preços globais
prices = {
    "BTCUSD": 0,
    "ETHUSD": 0,
    "XAUUSD": 0,
    "EURUSD": 0
}

# Atualiza preços da Coinbase
def update_coinbase():
    while True:
        try:
            btc = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot").json()
            eth = requests.get("https://api.coinbase.com/v2/prices/ETH-USD/spot").json()
            # XAUUSD aproximado via BTC/USD
            prices["BTCUSD"] = float(btc["data"]["amount"])
            prices["ETHUSD"] = float(eth["data"]["amount"])
            prices["XAUUSD"] = prices["BTCUSD"] / 25  # ajuste aproximado
        except Exception as e:
            print("Erro Coinbase:", e)
        time.sleep(60)

# Atualiza EURUSD via Alpha Vantage
def update_alpha_vantage():
    while True:
        try:
            url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=EUR&to_currency=USD&apikey={ALPHA_VANTAGE_API_KEY}"
            resp = requests.get(url).json()
            prices["EURUSD"] = float(resp["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
        except Exception as e:
            print("Erro Alpha Vantage:", e)
        time.sleep(60)

# Threads para atualização
threading.Thread(target=update_coinbase, daemon=True).start()
threading.Thread(target=update_alpha_vantage, daemon=True).start()

# Rotas
@app.route("/")
def dashboard():
    return render_template("dashboard.html", prices=prices)

@app.route("/api/prices")
def api_prices():
    return jsonify(prices)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
