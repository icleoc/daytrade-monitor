from flask import Flask, send_from_directory, jsonify
from monitor_vwap_real import start_background_thread, get_signals
import os

app = Flask(__name__, static_folder="static")

# Inicia thread de monitoramento
start_background_thread()

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/signals")
def signals():
    signals_data = get_signals()
    return jsonify(signals_data)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
