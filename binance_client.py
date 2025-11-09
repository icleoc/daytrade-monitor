# binance_client.py
import os
import time
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

BINANCE_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_API_SECRET")

_client = None
def get_client():
    global _client
    if _client is None:
        if not BINANCE_KEY or not BINANCE_SECRET:
            raise RuntimeError("BINANCE_API_KEY / BINANCE_API_SECRET não encontradas nas env vars.")
        _client = Client(BINANCE_KEY, BINANCE_SECRET)
    return _client

def fetch_binance_klines_df(symbol: str, interval: str = "2m", limit: int = 100, retry=3, backoff=1.2):
    client = get_client()
    attempt = 0
    while attempt < retry:
        try:
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
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
            df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
            return df
        except (BinanceAPIException, BinanceRequestException) as e:
            attempt += 1
            wait = backoff ** attempt
            print(f"Binance request error (attempt {attempt}/{retry}): {e}; sleeping {wait}s")
            time.sleep(wait)
        except Exception as e:
            print("Erro inesperado ao buscar klines da Binance:", e)
            raise
    raise RuntimeError("Falha ao obter klines da Binance após retries.")
