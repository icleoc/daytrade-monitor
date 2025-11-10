import datetime

def timestamp_now():
    return datetime.datetime.utcnow().isoformat() + "Z"

def clean_dataframe(df):
    return df.dropna().reset_index(drop=True)
# utils/helpers.py  (adicione ou atualize)
import numpy as np

def calc_vwap_from_ohlcv(ohlcv_list):
    """
    ohlcv_list: list of dicts with keys open, high, low, close, volume (oldest -> newest)
    Returns VWAP of the series (typical price weighted by volume).
    """
    if not ohlcv_list:
        return None
    typical = []
    vol = []
    for c in ohlcv_list:
        tp = (c["high"] + c["low"] + c["close"]) / 3.0
        typical.append(tp)
        vol.append(c.get("volume", 0.0))
    typical = np.array(typical, dtype=float)
    vol = np.array(vol, dtype=float)
    if vol.sum() == 0:
        return float(typical[-1])  # fallback last price
    vwap = (typical * vol).sum() / vol.sum()
    return float(vwap)
