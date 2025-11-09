import pandas as pd
import numpy as np

def run_monitor(data=None):
    if data is None:
        data = [
            {"price": 100, "volume": 10},
            {"price": 101, "volume": 15},
            {"price": 102, "volume": 20}
        ]
    df = pd.DataFrame(data)
    df["vwap"] = (df["price"] * df["volume"]).cumsum() / df["volume"].cumsum()
    return df.to_dict(orient="records")
