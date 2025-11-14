from flask import Flask, render_template, jsonify
import os
from helpers import fetch_all_symbols


app = Flask(__name__)


# Config
SYMBOLS = ["BTC/USDT", "ETH/USDT", "EUR/USD", "XAU/USD"]
UPDATE_INTERVAL_SECONDS = int(os.getenv("UPDATE_INTERVAL_SECONDS", "60"))


@app.route("/")
def dashboard():
# Pass minimal data to template; heavy data comes from /api/data
return render_template("dashboard.html", symbols=SYMBOLS, update_interval=UPDATE_INTERVAL_SECONDS)


@app.route("/api/data")
def api_data():
try:
data = fetch_all_symbols(SYMBOLS, interval="15m")
return jsonify(data)
except Exception as e:
return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
