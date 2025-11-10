# app.py
from flask import Flask, render_template
from monitor.monitor_vwap_real import get_assets_data

app = Flask(__name__)

# Lista de ativos a monitorar
ASSETS = ["WINM23.SA", "GC=F", "USDBRL=X"]

@app.route("/")
def dashboard():
    # Baixa os dados de forma robusta
    data = get_assets_data(ASSETS, interval='15m', period='7d')
    
    # Identifica ativos que falharam
    failed_assets = [asset for asset in ASSETS if asset not in data]

    return render_template(
        "dashboard.html",
        assets_data=data,
        failed_assets=failed_assets
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
