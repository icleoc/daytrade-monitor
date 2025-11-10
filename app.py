from flask import Flask, render_template, jsonify
import ccxt
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

app = Flask(__name__)

# Configura exchanges
coinbase = ccxt.coinbasepro()

# Lista de ativos
crypto_symbols = ['BTC/USD', 'ETH/USD']
forex_symbols = {'XAU/USD': 'GC=F', 'EUR/USD': 'EURUSD=X'}

# Função para buscar cripto
def get_crypto_prices():
    data = {}
    for symbol in crypto_symbols:
        ticker = coinbase.fetch_ticker(symbol)
        data[symbol] = ticker['last']
    return data

# Função para buscar Forex e XAU
def get_forex_prices():
    data = {}
    for key, yf_symbol in forex_symbols.items():
        ticker = yf.Ticker(yf_symbol)
        last_price = ticker.history(period="1d")['Close'][-1]
        data[key] = float(last_price)
    return data

# Função VWAP
def calculate_vwap(prices):
    df = pd.DataFrame(prices.items(), columns=['symbol', 'price'])
    df['volume'] = 1  # Simplificado: volume fictício
    vwap = (df['price'] * df['volume']).sum() / df['volume'].sum()
    return round(vwap, 2)

@app.route('/api/data')
def api_data():
    crypto = get_crypto_prices()
    forex = get_forex_prices()
    all_data = {**crypto, **forex}
    vwap = calculate_vwap(all_data)
    
    # Gerando sinais simples
    signals = {}
    for k, price in all_data.items():
        signals[k] = 'BUY' if price < vwap else 'SELL'
    
    return jsonify({
        'prices': all_data,
        'vwap': vwap,
        'signals': signals,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
