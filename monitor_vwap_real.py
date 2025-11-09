import os
import time
import threading
import requests
from flask import Flask, jsonify, render_template
from supabase import create_client, Client

# -----------------------------
# Variáveis de ambiente
# -----------------------------
ASSETS_COINBASE = os.environ.get("ASSETS", "BTC-USD,ETH-USD").split(",")
ASSETS_TWELVEDATA = ["EUR/USD", "XAU/USD"]
COINBASE_GRANULARITY = int(os.environ.get("COINBASE_GRANULARITY", 60))  # 1min por padrão
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 60))  # 60s por padrão
TWELVEDATA_API_KEY = os.environ.get("TWELVEDATA_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_TABLE = os.environ.get("SUPABASE_TABLE", "ativos")
SUPABASE_TABLE_SIGNALS = os.environ.get("SUPABASE_TABLE_SIGNALS", "sinais")

# -----------------------------
# Inicializa Supabase
# -----------------------------
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# Flask App
# -----------------------------
app = Flask(__name__)

# -----------------------------
# Dicionário global de sinais
# -----------------------------
current_signals = {asset: {"preco": None, "vwap": None, "sinal": "NEUTRO"} for asset in ASSETS_COINBASE + ASSETS_TWELVEDATA}

# -----------------------------
# Funções de fetch
# -----------------------------
def fetch_coinbase(asset):
    url = f"https://api.exchange.coinbase.com/products/{asset}/candles?granularity={COINBASE_GRANULARITY}"
    headers = {"User-Agent": "vwap-monitor"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        candles = resp.json()
        if not candles:
            return {"preco": None, "vwap": None, "sinal": "NEUTRO"}
        # VWAP simples: média ponderada pelo volume
        total_vol = sum(c[5] for c in candles)
        vwap = sum(c[4]*c[5] for c in candles)/total_vol
        preco = candles[-1][4]
        sinal = "COMPRA" if preco > vwap else "VENDA" if preco < vwap else "NEUTRO"
        return {"preco": preco, "vwap": vwap, "sinal": sinal}
    except Exception:
        return {"preco": None, "vwap": None, "sinal": "NEUTRO"}

def fetch_twelvedata(asset):
    symbol = asset.replace("/", "")
    interval = "1min"
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={TWELVEDATA_API_KEY}"
    try:
        resp = requests.get(url, timeout=10).json()
        if "values" not in resp or not resp["values"]:
            return {"preco": None, "vwap": None, "sinal": "NEUTRO"}
        candles = resp["values"]
        total_vol = sum(float(c.get("volume", 1)) for c in candles)
        vwap = sum(float(c["close"])*float(c.get("volume", 1)) for c in candles)/total_vol
        preco = float(candles[0]["close"])
        sinal = "COMPRA" if preco > vwap else "VENDA" if preco < vwap else "NEUTRO"
        return {"preco": preco, "vwap": vwap, "sinal": sinal}
    except Exception:
        return {"preco": None, "vwap": None, "sinal": "NEUTRO"}

# -----------------------------
# Loop principal do monitor
# -----------------------------
def monitor_loop():
    # Primeiro fetch antes de entrar no loop
    for asset in ASSETS_COINBASE:
        current_signals[asset] = fetch_coinbase(asset)
    for asset in ASSETS_TWELVEDATA:
        current_signals[asset] = fetch_twelvedata(asset)

    while True:
        for asset in ASSETS_COINBASE:
            current_signals[asset] = fetch_coinbase(asset)
        for asset in ASSETS_TWELVEDATA:
            current_signals[asset] = fetch_twelvedata(asset)
        time.sleep(POLL_INTERVAL)

def start_background_thread():
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()

# -----------------------------
# Rotas Flask
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/signals")
def api_signals():
    return jsonify(current_signals)

# -----------------------------
# Inicialização
# -----------------------------
if __name__ == "__main__":
    start_background_thread()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
