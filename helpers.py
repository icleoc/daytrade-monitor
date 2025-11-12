import requests
import pandas as pd
import os

API_KEY = os.getenv("TWELVE_API_KEY")

def get_twelvedata(symbol):
    url = f"https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": "1min",
        "outputsize": 100,
        "apikey": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "values" not in data:
        print(f"[ERROR] {symbol}: Sem dados válidos. Resposta:", data)
        return None

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    return df


def calculate_vwap(df):
    if df is None or df.empty:
        return None
    df["vwap"] = (df["volume"] * (df["high"] + df["low"] + df["close"]) / 3).cumsum() / df["volume"].cumsum()
    return df


def get_all_assets():
    assets = {
        "BTCUSD": "BTC/USD",
        "ETHUSD": "ETH/USD",
        "EURUSD": "EUR/USD",
        "XAUUSD": "XAU/USD"
    }

    results = {}
    for symbol, name in assets.items():
        df = get_twelvedata(symbol)
        df = calculate_vwap(df)
        if df is not None:
            results[symbol] = df
    return results
