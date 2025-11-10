import requests
import pandas as pd
import numpy as np
from config import CANDLE_LIMIT, TIMEFRAME_MINUTES

CRYPTOCOMPARE_URL = "https://min-api.cryptocompare.com/data/v2/histominute"
FOREX_URL = "https://api.exchangerate.host/timeseries"

def fetch_cryptocompare_candles(symbol, aggregate_minutes=15, limit=120):
    fsym, tsym = symbol[:3], symbol[3:]
    url = f"{CRYPTOCOMPARE_URL}?fsym={fsym}&tsym={tsym}&limit={limit}&aggregate={aggregate_minutes}"
    r = requests.get(url)
    data = r.json()
    if data.get("Response") != "Success":
        raise RuntimeError(f"Unexpected CryptoCompare response for {symbol}: {data}")
    df = pd.DataFrame(data["Data"]["Data"])
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

def fetch_forex_candles(symbol, limit=120):
    base, quote = symbol[:3], symbol[3:]
    url = f"{FOREX_URL}?start_date=2024-01-01&end_date=2025-11-10&base={base}&symbols={quote}"
    r = requests.get(url)
    data = r.json()
    if not data.get("rates"):
        raise RuntimeError(f"Unexpected Forex response for {symbol}: {data}")
    df = pd.DataFrame(list(data["rates"].items()), columns=["time", "rates"])
    df["close"] = df["rates"].apply(lambda x: list(x.values())[0])
    df["open"] = df["close"]
    df["high"] = df["close"]
    df["low"] = df["close"]
    df = df.tail(limit)
    df["time"] = pd.to_datetime(df["time"])
    return df[["time", "open", "high", "low", "close"]]

def compute_vwap_and_bands(df):
    df["typical"] = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = df["typical"].rolling(14).mean()
    df["upper"] = df["vwap"] + df["vwap"].rolling(14).std()
    df["lower"] = df["vwap"] - df["vwap"].rolling(14).std()
    return df

def compute_signal(df):
    last_close = df["close"].iloc[-1]
    last_vwap = df["vwap"].iloc[-1]
    if last_close > last_vwap:
        df.loc[df.index[-1], "signal_marker"] = "BUY"
        return "BUY"
    elif last_close < last_vwap:
        df.loc[df.index[-1], "signal_marker"] = "SELL"
        return "SELL"
    else:
        df.loc[df.index[-1], "signal_marker"] = None
        return "NEUTRAL"

def get_symbol_data(symbol):
    try:
        if symbol in ["BTCUSD", "ETHUSD"]:
            df = fetch_cryptocompare_candles(symbol, aggregate_minutes=TIMEFRAME_MINUTES, limit=CANDLE_LIMIT)
        else:
            df = fetch_forex_candles(symbol, limit=CANDLE_LIMIT)
        df = compute_vwap_and_bands(df)
        signal = compute_signal(df)
        return {
            "symbol": symbol,
            "price": float(df["close"].iloc[-1]),
            "signal": signal,
            "chart": df.tail(100).to_dict(orient="records"),
        }
    except Exception as e:
        raise RuntimeError(f"Error fetching candles for {symbol}: {e}")
