from flask import Flask, render_template, jsonify
from helpers import get_all_data

app = Flask(__name__)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "EURUSD", "XAUUSD"]

@app.route("/")
def dashboard():
    # Passa os símbolos para o template (serializáveis)
    return render_template("dashboard.html", symbols=SYMBOLS, update_interval=60)

@app.route("/api/data")
def api_data():
    try:
        data = get_all_data(SYMBOLS, timeframe="1h", lookback_days=7)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
