from flask import Flask, render_template, jsonify
import config
from helpers import get_all_symbols_data

app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "dashboard.html",
        symbols=config.SYMBOLS,
        update_interval=config.UPDATE_INTERVAL_SECONDS
    )


@app.route("/api/data")
def api_data():
    try:
        data = get_all_symbols_data(config.SYMBOLS)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
