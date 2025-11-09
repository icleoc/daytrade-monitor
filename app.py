from flask import Flask, jsonify, request
from supabase import create_client, Client
import os
import pandas as pd
import numpy as np
from monitor.monitor_vwap import run_vwap
from monitor.monitor_rsi import run_rsi
from monitor.monitor_macd import run_macd

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Sistema funcionando em Python 3.13.4"})

@app.route("/vwap")
def vwap():
    result = run_vwap()
    return jsonify(result)

@app.route("/rsi")
def rsi():
    result = run_rsi()
    return jsonify(result)

@app.route("/macd")
def macd():
    result = run_macd()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
