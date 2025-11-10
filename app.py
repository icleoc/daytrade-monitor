from flask import Flask, render_template
from monitor.monitor_vwap_real import get_assets_data, ASSETS

app = Flask(__name__)

@app.route("/")
def dashboard():
    df_dict = get_assets_data(ASSETS, interval='15m', period='7d')
    return render_template("dashboard.html", df_dict=df_dict)
