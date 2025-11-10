from flask import Flask, jsonify, render_template
from monitor.monitor_vwap_real import get_all_vwap_data
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/vwap')
def vwap_data():
    data = get_all_vwap_data()
    return jsonify(data)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Monitor VWAP em execução."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
import yfinance as yf

def get_yahoo_data(symbol, interval='1m', period='1d'):
    try:
        df = yf.download(tickers=symbol, interval=interval, period=period)
        if df.empty:
            return None
        df['vwap'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
        latest = df.iloc[-1]
        return {
            "symbol": symbol,
            "price": round(latest['Close'], 4),
            "vwap": round(latest['vwap'], 4),
            "time": str(latest.name)
        }
    except Exception as e:
        print(f"Erro ao buscar {symbol}: {e}")
        return None
