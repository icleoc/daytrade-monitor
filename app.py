from flask import Flask, render_template, jsonify
from helpers import get_all_symbols_data

app = Flask(__name__)

SYMBOLS = ["BTC/USDT", "ETH/USDT", "EUR/USD", "XAU/USD"]
UPDATE_INTERVAL_SECONDS = 60

@app.route("/")
def index():
    return render_template(
        "dashboard.html",
        symbols=SYMBOLS,
        update_interval=UPDATE_INTERVAL_SECONDS
    )

@app.route("/api/data")
def api_data():
    data = get_all_symbols_data(SYMBOLS)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
