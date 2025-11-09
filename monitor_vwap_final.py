import threading
import time
import os
import requests
import pandas as pd
from supabase import create_client, Client

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE_SIGNALS = os.getenv("SUPABASE_TABLE_SIGNALS")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
COINBASE_GRANULARITY = int(os.getenv("COINBASE_GRANULARITY", 300))  # segundos
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 10))  # segundos

ASSETS = os.getenv("ASSETS", "BTC-USD,ETH-USD,EUR/USD,XAU/USD").split(",")

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Global signals dictionary
signals_data = {asset: {"preco": None, "vwap": None, "sinal": "NEUTRO"} for asset in ASSETS}

def fetch_coinbase_candles(symbol, granularity):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={granularity}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        df = pd.DataFrame(data, columns=["time","low","high","open","close","volume"])
        df.sort_values("time", inplace=True)
        return df
    except Exception as e:
        print(f"Falha ao buscar candles Coinbase {symbol}: {e}")
        return None

def fetch_twelvedata_candles(symbol, interval="1min"):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={TWELVEDATA_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "values" not in data:
            return None
        df = pd.DataFrame(data["values"])
        df["close"] = pd.to_numeric(df["close"])
        return df
    except Exception as e:
        print(f"Falha ao buscar candles TwelveData {symbol}: {e}")
        return None

def calculate_vwap(df):
    if df is None or df.empty:
        return None
    df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (df["typical_price"] * df["volume"]).sum() / df["volume"].sum()
    return vwap

def update_signals():
    while True:
        for asset in ASSETS:
            if asset.endswith("-USD"):  # Crypto -> Coinbase
                df = fetch_coinbase_candles(asset, COINBASE_GRANULARITY)
            else:  # Forex/Gold -> TwelveData
                df = fetch_twelvedata_candles(asset, interval="1min")

            if df is not None:
                preco_atual = df["close"].iloc[-1]
                vwap = calculate_vwap(df)
                if preco_atual > vwap:
                    sinal = "COMPRA"
                elif preco_atual < vwap:
                    sinal = "VENDA"
                else:
                    sinal = "NEUTRO"
                signals_data[asset] = {"preco": preco_atual, "vwap": vwap, "sinal": sinal}
            else:
                signals_data[asset] = {"preco": None, "vwap": None, "sinal": "NEUTRO"}

        # Save signals to Supabase
        try:
            supabase.table(SUPABASE_TABLE_SIGNALS).upsert([
                {"id": 1, **signals_data}
            ]).execute()
        except Exception as e:
            print(f"Falha ao atualizar Supabase: {e}")

        time.sleep(POLL_INTERVAL)

def start_background_thread():
    thread = threading.Thread(target=update_signals, daemon=True)
    thread.start()

def get_signals():
    return signals_data
