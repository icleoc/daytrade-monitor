# binance_client.py
import os
from binance.client import Client
from datetime import datetime
import pandas as pd

BINANCE_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_API_SECRET")

_client = None
def get_client():
    global _client
    if _client is None:
        if not BINANCE_KEY or not BINANCE_SECRET:
            raise RuntimeError("Faltam BINANCE_API_KEY / BINANCE_API_SECRET nas env vars.")
        _client = Client(BINANCE_KEY, BINANCE_SECRET)
    return _client

def fetch_binance_klines_df(symbol: str, interval: str = "2m", limit: int = 100):
    client = get_client()
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        "open_time","open","high","low","close","volume","close_time","qav","num_trades",
        "taker_base","taker_quote","ignore"
    ])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    # convert times
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    return df
