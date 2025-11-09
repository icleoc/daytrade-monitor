import pandas as pd
import numpy as np
import requests
import os

def run_macd(short=12, long=26, signal=9):
    url = os.getenv("MARKET_API_URL")
    df = pd.DataFrame(requests.get(url).json())
    df["ema_short"] = df["price"].ewm(span=short, adjust=False).mean()
    df["ema_long"] = df["price"].ewm(span=long, adjust=False).mean()
    df["macd"] = df["ema_short"] - df["ema_long"]
    df["signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
    return df[["timestamp", "price", "macd", "signal"]].tail(10).to_dict(orient="records")
