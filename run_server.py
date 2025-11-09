from monitor_vwap_final import start_background_thread, get_signals
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

# Inicia thread de atualização contínua
start_background_thread()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/signals")
def api_signals():
    return jsonify(get_signals())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
