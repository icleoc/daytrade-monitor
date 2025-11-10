from flask import Flask, render_template, jsonify
from helpers import get_symbol_data
from config import SYMBOLS, UPDATE_INTERVAL_SECONDS

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("dashboard.html", symbols=SYMBOLS, update_interval=UPDATE_INTERVAL_SECONDS)

@app.route("/api/data")
def api_data():
    data = []
    for sym in SYMBOLS:
        data_obj = get_symbol_data(sym)
        data.append(data_obj)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
