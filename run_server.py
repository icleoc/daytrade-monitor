from flask import Flask, jsonify, render_template
from monitor_vwap_final import start_background_thread, get_signals
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# Start the background thread for updating signals
start_background_thread()

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/signals")
def api_signals():
    signals = get_signals()
    return jsonify(signals)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
