from flask import Flask, jsonify
from monitor_vwap_real import start_background_thread, get_current_signals

app = Flask(__name__)

# Inicia monitor em background
start_background_thread()

@app.route("/api/signals", methods=["GET"])
def api_signals():
    return jsonify(get_current_signals())

@app.route("/", methods=["GET"])
def home():
    return "<h2>VWAP Monitor Day Trade rodando!</h2><p>Acesse /api/signals para ver sinais em tempo real.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
