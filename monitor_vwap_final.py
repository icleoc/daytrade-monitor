import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime

def get_market_data():
    url = os.getenv("MARKET_API_URL")
    resp = requests.get(url)
    return pd.DataFrame(resp.json())

def calculate_vwap(df):
    df["vwap"] = (df["price"] * df["volume"]).cumsum() / df["volume"].cumsum()
    return df

def run_monitor():
    df = get_market_data()
    df = calculate_vwap(df)
    print(df.tail(5))

if __name__ == "__main__":
    run_monitor()
