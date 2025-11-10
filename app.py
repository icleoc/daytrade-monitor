# app.py

from flask import Flask, render_template
from monitor_vwap_real import binance_data, eurusd_data

app = Flask(__name__, template_folder="templates")  # pasta templates

@app.route("/")
def dashboard():
    return render_template("dashboard.html", binance_data=binance_data, eurusd_data=eurusd_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
