import pandas as pd
import numpy as np
import requests
import os

def get_market_data():
    url = os.getenv("MARKET_API_URL")
    resp = requests.get(url)
    df = pd.DataFrame(resp.json())
    return df

def calculate_vwap(df):
    df["vwap"] = (df["price"] * df["volume"]).cumsum() / df["volume"].cumsum()
    return df[["timestamp", "price", "vwap"]].tail(10).to_dict(orient="records")

def run_vwap():
    df = get_market_data()
    return calculate_vwap(df)
