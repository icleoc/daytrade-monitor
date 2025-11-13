import os
import requests
import pandas as pd
import numpy as np
import logging
from datetime import datetime

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")
TWELVE_BASE = "https://api.twelvedata.com/time_series"

SYMBOLS = {
    "BTCUSDT": {"symbol": "BTC/USD", "source": "twelve"},
    "ETHUSDT": {"symbol": "ETH/USD", "source": "twelve"},
    "EURUSD": {"symbol": "EUR/USD", "source": "twelve"},
    "XAUUSD": {"symbol": "XAU/USD", "source": "twelve"},
}

def get_vwap(df):
    df["TP"] = (df["high"] + df["low"] + df["close"]) / 3
    df["PV"] = df["TP"] * df["volume"]
    df["VWAP"] = df["PV"].cumsum() / df["volume"].cumsum()
    df["upper"] = df["VWAP"] * 1.0025
    df["lower"] = df["VWAP"] * 0.9975
    return df

def fetch_twelve_data(symbol, interval="15min"):
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": TWELVE_API_KEY,
        "outputsize": 100,
    }
    r = requests.get(TWELVE_BASE, params=params)
    r.raise_for_status()
    data = r.json()

    if "values" not in data:
        raise ValueError(data.get("message", "Sem dados da Twelve Data"))

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return get_vwap(df)

def generate_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    if last["close"] > last["upper"] and prev["close"] <= prev["upper"]:
        signal = "SELL"
    elif last["close"] < last["lower"] and prev["close"] >= prev["lower"]:
        signal = "BUY"
    else:
        signal = "HOLD"

    return signal

def get_all_data():
    results = {}
    for key, info in SYMBOLS.items():
        try:
            df = fetch_twelve_data(info["symbol"], interval="15min")
            signal = generate_signal(df)
            results[key] = {
                "last_price": round(df["close"].iloc[-1], 5),
                "signal": signal,
                "latest": df.tail(50).to_dict(orient="records"),
            }
        except Exception as e:
            logger.error(f"Erro ao buscar {key}: {e}")
            results[key] = {"error": str(e)}

    return results
