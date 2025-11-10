# app.py
from flask import Flask, jsonify, render_template
from monitor.monitor_vwap_real import get_all_vwap_data
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/vwap")
def api_vwap():
    data = get_all_vwap_data()
    return jsonify({"assets": data})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
