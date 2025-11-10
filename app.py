from flask import Flask, render_template, jsonify
from coinbase.wallet.client import Client as CoinbaseClient
import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# --- CHAVES (você adiciona direto no Render) ---
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY")
COINBASE_API_SECRET = os.getenv("COINBASE_API_SECRET")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

coinbase_client = CoinbaseClient(COINBASE_API_KEY, COINBASE_API_SECRET)

# --- FUNÇÃO PARA BUSCAR PREÇOS ATUAIS ---
def get_prices():
    prices = {}
    # BTC/USD
    prices['BTC'] = float(coinbase_client.get_spot_price(currency_pair='BTC-USD')['amount'])
    # ETH/USD
    prices['ETH'] = float(coinbase_client.get_spot_price(currency_pair='ETH-USD')['amount'])
    # XAU/USD
    prices['XAU'] = float(coinbase_client.get_spot_price(currency_pair='XAU-USD')['amount'])
    # EUR/USD via Alpha Vantage
    url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=EUR&to_currency=USD&apikey={ALPHA_VANTAGE_API_KEY}'
    r = requests.get(url).json()
    prices['EUR'] = float(r["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
    return prices

# --- FUNÇÃO VWAP SIMPLIFICADA ---
def calculate_vwap(prices_history):
    df = pd.DataFrame(prices_history)
    df['vwap'] = (df['price'] * df['volume']).cumsum() / df['volume'].cumsum()
    return df['vwap'].iloc[-1]

# --- ROTA DASHBOARD ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# --- API DE PREÇOS ---
@app.route('/api/prices')
def api_prices():
    prices = get_prices()
    # Simulando histórico para VWAP
    prices_history = [{'price': v, 'volume': 1} for v in prices.values()]
    vwap = {k: calculate_vwap([{'price': v, 'volume': 1}]) for k, v in prices.items()}
    return jsonify({'prices': prices, 'vwap': vwap})

# --- ROTA HISTÓRICO PARA GRÁFICO ---
@app.route('/api/historical/<symbol>')
def api_historical(symbol):
    # Dummy data para gráfico, 30 pontos
    now = datetime.utcnow()
    data = [{'time': (now - timedelta(minutes=i)).strftime('%H:%M'), 'price': np.random.uniform(90, 110)} for i in range(30)][::-1]
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
