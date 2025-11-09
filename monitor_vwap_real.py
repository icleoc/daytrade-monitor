import os
import time
import threading
import requests
from datetime import datetime
from supabase import create_client, Client

# Variáveis de ambiente
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_TABLE = os.environ.get("SUPABASE_TABLE")
SUPABASE_TABLE_SIGNALS = os.environ.get("SUPABASE_TABLE_SIGNALS")
TWELVEDATA_API_KEY = os.environ.get("TWELVEDATA_API_KEY")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 60))
COINBASE_GRANULARITY = int(os.environ.get("COINBASE_GRANULARITY", 60))
ASSETS = os.environ.get("ASSETS", "BTC-USD,ETH-USD,EUR/USD,XAU/USD").split(',')

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Armazena sinais atuais
current_signals = {asset: {"preco": None, "vwap": None, "sinal": "NEUTRO"} for asset in ASSETS}

# Funções para VWAP
def fetch_coinbase_candles(symbol, granularity):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={granularity}"
    headers = {"Accept": "application/json"}
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        # Coinbase retorna [time, low, high, open, close, volume], vamos usar close
        closes = [c[4] for c in data]
        vwap = sum(closes) / len(closes)
        preco = closes[-1]
        return preco, vwap
    except:
        return None

def fetch_twelvedata_candles(symbol):
    interval = os.environ.get("VWAP_CANDLES", "1min")
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={TWELVEDATA_API_KEY}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        values = data.get("values")
        if not values:
            return None
        closes = [float(v["close"]) for v in values]
        vwap = sum(closes) / len(closes)
        preco = closes[0]
        return preco, vwap
    except:
        return None

def upsert_signal(asset, preco, vwap, sinal):
    current_signals[asset] = {"preco": preco, "vwap": vwap, "sinal": sinal}
    try:
        payload = {
            "nome": asset,
            "preco": preco,
            "vwap": vwap,
            "sinal": sinal,
            "updated_at": datetime.utcnow().isoformat()
        }
        supabase.table(SUPABASE_TABLE_SIGNALS).upsert(payload, on_conflict="nome").execute()
    except:
        pass

def calculate_signal(preco, vwap):
    if preco is None or vwap is None:
        return "NEUTRO"
    if preco > vwap:
        return "VENDA"
    elif preco < vwap:
        return "COMPRA"
    else:
        return "NEUTRO"

def monitor_loop():
    while True:
        for asset in ASSETS:
            if "/" in asset:  # EUR/USD ou XAU/USD -> TwelveData
                result = fetch_twelvedata_candles(asset)
            else:  # BTC-USD, ETH-USD -> Coinbase
                result = fetch_coinbase_candles(asset, COINBASE_GRANULARITY)
            if result:
                preco, vwap = result
            else:
                preco = vwap = None
            sinal = calculate_signal(preco, vwap)
            upsert_signal(asset, preco, vwap, sinal)
        time.sleep(POLL_INTERVAL)

def start_background_thread():
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
