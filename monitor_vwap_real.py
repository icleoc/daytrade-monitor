# monitor_vwap_real.py
import os
import time
import requests
import pandas as pd
from flask import Flask, render_template, jsonify
from supabase import create_client, Client
from datetime import datetime, timezone

# ---------------------
# Configurações
# ---------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TWELVEDATA_KEY = os.getenv("TWELVEDATA_API_KEY")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 30))

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__, template_folder="templates")

# Pares
COINBASE_ASSETS = ["BTC-USD", "ETH-USD"]
TWELVEDATA_ASSETS = ["EUR/USD", "XAU/USD"]

# ---------------------
# Funções de dados
# ---------------------
def coinbase_get_candles(symbol, granularity=120):
    url = f"https://api.coinbase.com/api/v3/brokerage/products/{symbol}/candles?granularity={granularity}"
    headers = {"User-Agent": "VWAP-Monitor/1.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    if "candles" not in data or not data["candles"]:
        raise ValueError(f"Nenhum candle de Coinbase para {symbol}")
    df = pd.DataFrame(data["candles"])
    df = df.rename(columns={"start": "time"})
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    for c in ["low", "high", "open", "close", "volume"]:
        df[c] = df[c].astype(float)
    df = df.sort_values("time").reset_index(drop=True)
    return df

def coinbase_get_price(symbol):
    url = f"https://api.coinbase.com/v2/prices/{symbol}/spot"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    data = r.json()
    return float(data["data"]["amount"])

def twelvedata_get_candles(symbol, interval="2min", outputsize=50):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={TWELVEDATA_KEY}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    if "values" not in data or not data["values"]:
        raise ValueError(f"Nenhum candle TwelveData para {symbol}")
    df = pd.DataFrame(data["values"])
    df["time"] = pd.to_datetime(df["datetime"])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    df = df.sort_values("time").reset_index(drop=True)
    return df

def twelvedata_get_price(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVEDATA_KEY}"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    data = r.json()
    return float(data["price"])

def compute_vwap(df):
    if df.empty:
        return None
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    tp_vol = tp * df["volume"]
    denom = df["volume"].sum()
    if denom == 0:
        return None
    return tp_vol.sum() / denom

def upsert_supabase(symbol, price, vwap, signal):
    payload = {
        "nome": symbol,
        "preco": round(float(price), 6) if price else None,
        "vwap": round(float(vwap), 6) if vwap else None,
        "sinal": signal,
        "atualizado_em": datetime.now(timezone.utc).isoformat()
    }
    try:
        supabase.table("ativos").upsert(payload, on_conflict="nome").execute()
    except Exception as e:
        print(f"Erro ao upsert {symbol}: {e}")

# ---------------------
# Loop principal
# ---------------------
def start_bot():
    print(f"Iniciando VWAP Monitor em tempo real. Intervalo {REFRESH_INTERVAL}s")
    while True:
        # Coinbase
        for symbol in COINBASE_ASSETS:
            try:
                df = coinbase_get_candles(symbol)
                vwap = compute_vwap(df)
                last_price = coinbase_get_price(symbol)
                signal = "BUY" if last_price > vwap else "SELL"
                upsert_supabase(symbol, last_price, vwap, signal)
                print(f"{symbol} -> {signal} | price={last_price} vwap={vwap}")
            except Exception as e:
                print(f"Erro Coinbase {symbol}: {e}")

        # TwelveData
        for symbol in TWELVEDATA_ASSETS:
            try:
                df = twelvedata_get_candles(symbol)
                vwap = compute_vwap(df)
                last_price = twelvedata_get_price(symbol)
                signal = "BUY" if last_price > vwap else "SELL"
                upsert_supabase(symbol, last_price, vwap, signal)
                print(f"{symbol} -> {signal} | price={last_price} vwap={vwap}")
            except Exception as e:
                print(f"Erro TwelveData {symbol}: {e}")

        time.sleep(REFRESH_INTERVAL)

# ---------------------
# Flask endpoints
# ---------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/signals")
def api_signals():
    try:
        resp = supabase.table("ativos").select("*").execute()
        return jsonify(resp.data or [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    start_bot()
