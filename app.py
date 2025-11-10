# app.py
import traceback
from flask import Flask, render_template, jsonify
from config import SYMBOLS, UPDATE_INTERVAL_SECONDS
from helpers import get_symbol_data

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    # Pass symbol list to frontend
    return render_template("dashboard.html", symbols=SYMBOLS, update_interval=UPDATE_INTERVAL_SECONDS)

@app.route("/api/data")
def api_data():
    results = {}
    errors = {}
    for sym in SYMBOLS:
        try:
            # sym is like "BTCUSD"
            data_obj = get_symbol_data(sym)
            results[sym] = data_obj
        except Exception as e:
            # capture error and keep service alive
            err = f"{e}"
            errors[sym] = err
            results[sym] = {"data": [], "signal": {"signal": "ERROR", "reason": err, "time": None}}
            # print stack for Render logs
            print(f"[ERROR] {sym}: {err}")
            traceback.print_exc()
    return jsonify({"results": results, "errors": errors})

if __name__ == "__main__":
    # dev server
    app.run(host="0.0.0.0", port=5000)
