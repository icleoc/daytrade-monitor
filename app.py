from flask import Flask, jsonify, request
from supabase import create_client, Client
import os
from monitor import monitor_vwap

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Sistema funcionando em Python 3.13.4"})

@app.route("/run-monitor", methods=["POST"])
def run_monitor():
    data = request.json or {}
    result = monitor_vwap.run_monitor(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
