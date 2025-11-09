import threading
import time
import os
import requests
from datetime import datetime, timezone
from supabase import create_client, Client

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE_SIGNALS = os.getenv("SUPABASE_TABLE_SIGNALS", "signals")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ativos
ASSETS = os.getenv("ASSETS", "BTC-USD,ETH-USD,EUR/USD,XAU/USD").split(",")

# Coinbase
COINBASE_GRANULARITY = int(os.getenv("COINBASE_GRANULARITY", 60))  # em segundos

# Twelve Data
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
VWAP_CANDLES = os.getenv("VWAP_CANDLES", "1min")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))  # segundos

# Estado dos sinais
signals_state = {asset: {"preco": None, "vwap": None, "sinal": "NEUTRO"} for asset in ASSETS}

# Funções
def fetch_coinbase_candles(symbol, granularity):
    try:
        url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={granularity}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        return data
    except:
        return None

def fetch_twelvedata(symbol, interval):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={TWELVEDATA_API_KEY}&outputsize=10"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if "values" in data:
            return data["values"]
        return None
    except:
        return None

def calculate_vwap(candles):
    if not candles:
        return None
    # candles = [[time, low, high, open, close, volume], ...]
    total_vol = total_vol_price = 0
    for c in candles:
        if isinstance(c, dict):  # Twelve Data
            close = float(c["close"])
            vol = float(c["volume"])
        else:  # Coinbase
            close = c[4]
            vol = c[5]
        total_vol += vol
        total_vol_price += close * vol
    return total_vol_price / total_vol if total_vol else None

def determine_signal(price, vwap):
    if price is None or vwap is None:
        return "NEUTRO"
    if price > vwap:
        return "VENDA"
    elif price < vwap:
        return "COMPRA"
    else:
        return "NEUTRO"

def update_signals():
    global signals_state
    while True:
        for asset in ASSETS:
            if asset.endswith("USD") and "/" in asset:
                # Forex / Commodities via Twelve Data
                candles = fetch_twelvedata(asset.replace("/", ""), VWAP_CANDLES)
            else:
                # Cripto via Coinbase
                candles = fetch_coinbase_candles(asset, COINBASE_GRANULARITY)

            vwap = calculate_vwap(candles)
            if candles:
                if isinstance(candles[0], dict):
                    price = float(candles[0]["close"])
                else:
                    price = candles[0][4]
            else:
                price = None

            sinal = determine_signal(price, vwap)

            signals_state[asset] = {"preco": price, "vwap": vwap, "sinal": sinal}

        # Upsert no Supabase
        try:
            for asset, data in signals_state.items():
                supabase.table(SUPABASE_TABLE_SIGNALS).upsert(
                    {"nome": asset, "preco": data["preco"], "vwap": data["vwap"], "sinal": data["sinal"]}
                ).execute()
        except:
            pass

        time.sleep(POLL_INTERVAL)

def start_background_thread():
    t = threading.Thread(target=update_signals, daemon=True)
    t.start()

def get_signals():
    return signals_state
