import os
import threading
import time
import requests
import pandas as pd
from supabase import create_client, Client

# Configurações
ASSETS = os.environ.get("ASSETS", "BTC-USD,ETH-USD,EUR/USD,XAU/USD").split(",")
COINBASE_GRANULARITY = int(os.environ.get("COINBASE_GRANULARITY", 60))  # segundos
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 60))  # segundos
TWELVEDATA_API_KEY = os.environ.get("TWELVEDATA_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_TABLE_SIGNALS = os.environ.get("SUPABASE_TABLE_SIGNALS", "sinais")

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Armazena sinais atuais e últimos valores válidos
signals = {asset: {"preco": None, "vwap": None, "sinal": "NEUTRO"} for asset in ASSETS}

def fetch_coinbase_candles(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={COINBASE_GRANULARITY}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        df = pd.DataFrame(data, columns=["time", "low", "high", "open", "close", "volume"])
        df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
        latest = df.iloc[-1]
        return {"preco": latest["close"], "vwap": latest["vwap"]}
    except:
        return None

def fetch_tw_data(symbol):
    interval = "1min"
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={TWELVEDATA_API_KEY}&outputsize=20"
    try:
        r = requests.get(url).json()
        values = r.get("values")
        if not values:
            return None
        df = pd.DataFrame(values)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)
        df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
        latest = df.iloc[0]
        return {"preco": latest["close"], "vwap": latest["vwap"]}
    except:
        return None

def calculate_signal(preco, vwap):
    if preco is None or vwap is None:
        return "NEUTRO"
    if preco > vwap:
        return "COMPRA"
    elif preco < vwap:
        return "VENDA"
    return "NEUTRO"

def update_signals():
    while True:
        for asset in ASSETS:
            result = None
            if asset in ["BTC-USD", "ETH-USD"]:
                result = fetch_coinbase_candles(asset)
            else:
                result = fetch_tw_data(asset)

            # Mantém último valor válido se falhar
            preco = result["preco"] if result else signals[asset]["preco"]
            vwap = result["vwap"] if result else signals[asset]["vwap"]
            sinal = calculate_signal(preco, vwap)

            signals[asset] = {"preco": preco, "vwap": vwap, "sinal": sinal}

            # Persistência no Supabase
            payload = {"nome": asset, "preco": preco, "vwap": vwap, "sinal": sinal}
            try:
                supabase.table(SUPABASE_TABLE_SIGNALS).upsert(payload, on_conflict=["nome"]).execute()
            except:
                pass

        time.sleep(POLL_INTERVAL)

def start_background_thread():
    thread = threading.Thread(target=update_signals, daemon=True)
    thread.start()

def get_signals():
    return signals
