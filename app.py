from flask import Flask, jsonify, render_template
import random

app = Flask(__name__)

@app.route('/')
def home():
    # Renderiza o dashboard
    return render_template('dashboard.html')

@app.route('/vwap')
def get_vwap():
    # Exemplo simples de dado dinâmico
    vwap_value = round(random.uniform(9.8, 10.2), 4)
    return jsonify({"vwap": vwap_value})

@app.route('/rsi')
def get_rsi():
    rsi_value = round(random.uniform(30, 70), 2)
    return jsonify({"rsi": rsi_value})

@app.route('/macd')
def get_macd():
    macd_value = round(random.uniform(-1, 1), 3)
    return jsonify({"macd": macd_value})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
