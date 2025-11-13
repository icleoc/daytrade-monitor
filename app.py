from flask import Flask, render_template, jsonify
import config
from helpers import get_all_data
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def dashboard():
    # pass symbols to template (will be JSON-encoded)
    return render_template("dashboard.html", symbols=config.SYMBOLS, update_interval=config.UPDATE_INTERVAL_SECONDS)

@app.route("/api/data")
def api_data():
    try:
        data = get_all_data(config.SYMBOLS, interval="15m", limit=200)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
