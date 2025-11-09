import pandas as pd
import numpy as np
import requests
import os

def run_rsi(period: int = 14):
    url = os.getenv("MARKET_API_URL")
    df = pd.DataFrame(requests.get(url).json())
    delta = df["price"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))
    return df[["timestamp", "price", "rsi"]].tail(10).to_dict(orient="records")
