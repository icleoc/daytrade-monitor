from flask import Flask, jsonify, render_template
from monitor.monitor_vwap_real import get_all_vwap_data

# Instância única do app
app = Flask(__name__, static_folder="static", template_folder="templates")

# ---- Rotas ----

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/vwap")
def api_vwap():
    data = get_all_vwap_data()
    return jsonify({"assets": data})

# ---- Execução local ----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
