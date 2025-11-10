import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime

from config import TIMEFRAME_MINUTES, CANDLE_LIMIT

CRYPTOCOMPARE_URL = "https://min-api.cryptocompare.com/data/v2/histominute"
TWELVE_DATA_URL = "https://api.twelvedata.com/time_series"
TWELVE_API_KEY = os.getenv("TWELVE_API_KEY", "34b1f0bac586484c97725bbbbddad099")  # coloque sua chave real

def fetch_candles(symbol, aggregate_minutes=TIMEFRAME_MINUTES, limit=CANDLE_LIMIT):
    """Seleciona a fonte de dados automaticamente (cripto ou forex)"""
    if symbol in ["BTCUSD", "ETHUSD", "SOLUSD"]:
        return fetch_cryptocompare(symbol, aggregate_minutes, limit)
    else:
        return fetch_twelvedata(symbol, aggregate_minutes, limit)

def fetch_cryptocompare(symbol, aggregate_minutes, limit):
    url = f"{CRYPTOCOMPARE_URL}?fsym={symbol[:-3]}&tsym=USD&limit={limit}&aggregate={aggregate_minutes}"
    r = requests.get(url)
    data = r.json()
    if data.get("Response") != "Success":
        raise RuntimeError(f"Unexpected CryptoCompare response for {symbol}: {data}")
    df = pd.DataFrame(data["Data"]["Data"])
    df["datetime"] = pd.to_datetime(df["time"], unit="s")
    return df

def fetch_twelvedata(symbol, aggregate_minutes, limit):
    params = {
        "symbol": symbol,
        "interval": f"{aggregate_minutes}min",
        "apikey": TWELVE_API_KEY,
        "outputsize": limit
    }
    r = requests.get(TWELVE_DATA_URL, params=params)
    data = r.json()
    if "values" not in data:
        raise RuntimeError(f"Unexpected TwelveData response for {symbol}: {data}")
    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volumefrom"] = df["volume"].astype(float)
    return df[::-1].reset_index(drop=True)

def calculate_vwap(df):
    df["vwap"] = (df["close"] * df["volumefrom"]).cumsum() / df["volumefrom"].cumsum()
    return df

def get_symbol_data(symbol):
    try:
        df = fetch_candles(symbol)
        df = calculate_vwap(df)
        last = df.iloc[-1]
        return {
            "symbol": symbol,
            "price": float(last["close"]),
            "vwap": float(last["vwap"]),
            "timestamp": last["datetime"].isoformat(),
            "trend": "bullish" if last["close"] > last["vwap"] else "bearish",
            "df": df.tail(50).to_dict(orient="records")
        }
    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}
