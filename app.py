from flask import Flask, render_template
from monitor.monitor_vwap_real import get_assets_data

app = Flask(__name__)

# Ativos reais do Brasil (índice futuro, dólar, ouro, etc.)
ASSETS = ["^BVSP", "USDBRL=X", "GC=F"]  

@app.route("/")
def dashboard():
    try:
        data = get_assets_data(ASSETS, interval='15m', period='7d')
    except Exception as e:
        print("Erro ao obter dados:", e)
        data = {}  # evita quebrar o template

    return render_template("dashboard.html", df=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
