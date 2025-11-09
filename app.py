from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "API do Monitor VWAP funcionando!"})

@app.route('/vwap')
def vwap():
    # Exemplo simples de cálculo de VWAP com dados mockados
    trades = [
        {"price": 10.0, "volume": 100},
        {"price": 10.2, "volume": 150},
        {"price": 9.9, "volume": 200}
    ]
    total_value = sum(t["price"] * t["volume"] for t in trades)
    total_volume = sum(t["volume"] for t in trades)
    vwap_value = total_value / total_volume if total_volume > 0 else 0
    return jsonify({"vwap": round(vwap_value, 4)})

@app.route('/rsi')
def rsi():
    prices = [10, 11, 12, 11, 10, 9, 10, 11, 12, 11, 10]
    gains = [max(prices[i+1] - prices[i], 0) for i in range(len(prices)-1)]
    losses = [max(prices[i] - prices[i+1], 0) for i in range(len(prices)-1)]
    avg_gain = sum(gains)/len(gains)
    avg_loss = sum(losses)/len(losses)
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi_value = 100 - (100 / (1 + rs))
    return jsonify({"rsi": round(rsi_value, 2)})

@app.route('/macd')
def macd():
    prices = [10, 10.5, 10.8, 10.3, 10.0, 9.8, 10.2, 10.6, 11.0]
    short_ema = sum(prices[-5:]) / 5
    long_ema = sum(prices[-9:]) / 9
    macd_value = short_ema - long_ema
    return jsonify({"macd": round(macd_value, 4)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
