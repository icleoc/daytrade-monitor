from flask import Flask, jsonify, render_template
from helpers import get_asset_data
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/api/data")
def api_data():
    assets = ["BTCUSDT", "ETHUSDT", "EUR/USD", "XAU/USD"]
    interval = "1h"

    response_data = {}
    for symbol in assets:
        df = get_asset_data(symbol, interval)
        if not df.empty:
            response_data[symbol] = {
                "times": df["open_time"].astype(str).tolist(),
                "prices": df["close"].tolist()
            }
        else:
            response_data[symbol] = {"error": "Sem dados"}
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
