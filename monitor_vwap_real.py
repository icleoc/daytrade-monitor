import time
import threading
import requests
import pandas as pd
from datetime import datetime, timezone
from flask import Flask, jsonify
from supabase import create_client, Client

# ===================== CONFIGURAÇÕES =====================
SUPABASE_URL = "COLE_AQUI_SEU_SUPABASE_URL"
SUPABASE_KEY = "COLE_AQUI_SEU_SUPABASE_KEY"
TWELVEDATA_KEY = "COLE_AQUI_SUA_TWELVEDATA_KEY"

ASSETS_COINBASE = ["BTC-USD", "ETH-USD"]
ASSETS_TWELVE = ["EUR/USD", "XAU/USD"]

INTERVAL_COINBASE = 60  # segundos (1 minuto)
INTERVAL_TWELVE = "1min"

REFRESH_TIME = 60  # segundos entre atualizações

# Criação do cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===================== FUNÇÕES =====================

def fetch_coinbase_candles(symbol):
    """Busca candles da Coinbase (1min)"""
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={INTERVAL_COINBASE}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=["time","low","high","open","close","volume"])
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        return df
    except Exception as e:
        print(f"[WARNING] Falha ao buscar candles Coinbase {symbol}: {e}")
        return None

def fetch_twelfthdata_candles(symbol):
    """Busca candles do TwelveData (1min)"""
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={INTERVAL_TWELVE}&outputsize=100&apikey={TWELVEDATA_KEY}"
    try:
        r = requests.get(url, timeout=10).json()
        if "values" not in r:
            print(f"[WARNING] TwelveData retornou sem 'values' para {symbol}: {r}")
            return None
        df = pd.DataFrame(r["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.rename(columns={"open":"open","high":"high","low":"low","close":"close","volume":"volume"})
        df = df[["datetime","open","high","low","close","volume"]]
        df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)
        return df
    except Exception as e:
        print(f"[WARNING] Falha ao buscar candles TwelveData {symbol}: {e}")
        return None

def calculate_vwap(df):
    """Calcula VWAP"""
    try:
        df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
        vwap = (df["typical_price"] * df["volume"]).sum() / df["volume"].sum()
        return vwap
    except:
        return None

def generate_signal(price, vwap):
    """Define sinal de compra/venda/neutro"""
    if price is None or vwap is None:
        return "NEUTRO"
    if price > vwap:
        return "VENDA"
    elif price < vwap:
        return "COMPRA"
    else:
        return "NEUTRO"

def get_signals():
    """Retorna sinais atualizados para todos os ativos"""
    signals = {}

    # Coinbase
    for asset in ASSETS_COINBASE:
        df = fetch_coinbase_candles(asset)
        if df is not None and not df.empty:
            price = df["close"].iloc[-1]
            vwap = calculate_vwap(df)
            signal = generate_signal(price, vwap)
        else:
            price = None
            vwap = None
            signal = "NEUTRO"
        signals[asset] = {"preco": price, "vwap": vwap, "sinal": signal}

    # TwelveData
    for asset in ASSETS_TWELVE:
        df = fetch_twelfthdata_candles(asset)
        if df is not None and not df.empty:
            price = df["close"].iloc[-1]
            vwap = calculate_vwap(df)
            signal = generate_signal(price, vwap)
        else:
            price = None
            vwap = None
            signal = "NEUTRO"
        signals[asset] = {"preco": price, "vwap": vwap, "sinal": signal}

    return signals

def upsert_ativo(nome, preco, vwap, sinal):
    """Atualiza ou insere ativo no Supabase"""
    payload = {"nome": nome, "preco": preco, "vwap": vwap, "sinal": sinal}
    try:
        supabase.table("ativos").upsert(payload, on_conflict="nome").execute()
    except Exception as e:
        print(f"[ERROR] Erro ao upsertar no Supabase para {nome}: {e}")

def background_loop():
    """Loop principal em thread separada"""
    while True:
        signals = get_signals()
        for nome, dados in signals.items():
            upsert_ativo(nome, dados["preco"], dados["vwap"], dados["sinal"])
        time.sleep(REFRESH_TIME)

# ===================== FLASK =====================
app = Flask(__name__)

@app.route("/api/signals")
def api_signals():
    signals = get_signals()
    return jsonify(signals)

def start_background_thread():
    t = threading.Thread(target=background_loop, daemon=True)
    t.start()

# ===================== INICIALIZAÇÃO =====================
if __name__ == "__main__":
    print("Iniciando VWAP Monitor (Coinbase + TwelveData)...")
    start_background_thread()
    app.run(host="0.0.0.0", port=5000)
