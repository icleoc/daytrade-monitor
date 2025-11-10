# helpers.py
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from config import BASE_URL, CRYPTOCOMPARE_API_KEY

def fetch_crypto_compare_histo(symbol: str, limit: int = 200) -> pd.DataFrame:
    """Busca histórico de candles via CryptoCompare API."""
    url = f"{BASE_URL}/v2/histohour?fsym={symbol[:-4]}&tsym={symbol[-4:]}&limit={limit}&api_key={CRYPTOCOMPARE_API_KEY}"
    r = requests.get(url)
    data = r.json()
    if "Data" not in data or "Data" not in data["Data"]:
        raise ValueError(f"Resposta inesperada da API para {symbol}: {data}")

    df = pd.DataFrame(data["Data"]["Data"])
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

def compute_vwap_and_bands(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula VWAP e bandas."""
    df["tp"] = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (df["tp"] * df["volumefrom"]).cumsum() / df["volumefrom"].cumsum()
    df["upper_band"] = df["vwap"] + df["tp"].rolling(14).std()
    df["lower_band"] = df["vwap"] - df["tp"].rolling(14).std()
    return df

def compute_signal(df: pd.DataFrame) -> str:
    """Retorna sinal de compra/venda com base no VWAP."""
    close = df["close"].iloc[-1]
    vwap = df["vwap"].iloc[-1]
    if close > vwap:
        return "BUY"
    elif close < vwap:
        return "SELL"
    return "NEUTRAL"
