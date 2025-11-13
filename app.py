from flask import Flask, render_template, jsonify
from helpers import get_market_data
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/data")
def api_data():
    try:
        data = get_market_data()
        if not data:
            return jsonify({"error": "Sem dados disponíveis"}), 500
        return jsonify(data)
    except Exception as e:
        logger.error(f"Erro na API: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
