# app.py
from flask import Flask, render_template, jsonify
from config import SYMBOLS, UPDATE_INTERVAL_SECONDS

# Import deve vir após config, e precisamos importar a função explicitamente
import helpers

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    symbols = [s["symbol"] for s in SYMBOLS]
    return render_template("dashboard.html", symbols=symbols, update_interval=UPDATE_INTERVAL_SECONDS)

@app.route("/api/data")
def api_data():
    payload = []
    for s in SYMBOLS:
        sym = s["symbol"]
        td = s.get("td_symbol", sym)
        data_obj = helpers.get_symbol_data(sym, td)
        if data_obj is not None:
            payload.append(data_obj)
        else:
            payload.append({"symbol": sym, "error": "no_data"})
    return jsonify(payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
