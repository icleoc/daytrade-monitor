from flask import Flask, jsonify, render_template
from monitor.monitor_vwap_real import get_all_assets_data

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/vwap")
def vwap_data():
    data = get_all_assets_data()
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
