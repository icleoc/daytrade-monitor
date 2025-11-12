from flask import Flask, jsonify, render_template
from helpers import get_symbol_data
from config import SYMBOLS

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html', symbols=SYMBOLS)

@app.route('/api/data')
def api_data():
    data = []
    for sym in SYMBOLS:
        try:
            info = get_symbol_data(sym["symbol"])
            data.append(info)
        except Exception as e:
            print(f"[ERROR] {sym['symbol']}: {e}")
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
