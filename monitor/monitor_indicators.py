import pandas as pd
import numpy as np

def moving_average(df, period=5):
    df["ma"] = df["price"].rolling(period).mean()
    return df
