# helpers.py
import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from config import (
    CRYPTOCOMPARE_BASE,
    CRYPTOCOMPARE_API_KEY,
    TIMEFRAME_MINUTES,
    CANDLE_LIMIT,
)

HEADERS = {"authorization": f"Apikey {CRYPTOCOMPARE_API_KEY}"} if CRYPTOCOMPARE_API_KEY else {}

def _split_symbol(sym: str):
    """
    Given symbol like 'BTCUSD' -> returns ('BTC', 'USD')
    Works for XAUUSD and EURUSD as well.
    """
    # Common FX/commodity symbols are 6 chars (EURUSD) or XAUUSD (5?), we assume last 3 are quote (USD)
    base = sym[:-3]
    quote = sym[-3:]
    return base.upper(), quote.upper()

def fetch_cryptocompare_candles(symbol: str, aggregate_minutes: int = TIMEFRAME_MINUTES, limit: int = CANDLE_LIMIT) -> pd.DataFrame:
    """
    Fetch candles using CryptoCompare histominute endpoint with aggregate.
    Returns DataFrame with columns: datetime, open, high, low, close, volume
    Raises RuntimeError on API error.
    """
    base, quote = _split_symbol(symbol)
    url = f"{CRYPTOCOMPARE_BASE}/histominute"
    params = {
        "fsym": base,
        "tsym": quote,
        "aggregate": aggregate_minutes,
        "limit": limit - 1,
        "e": "CCCAGG"
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    # CryptoCompare v2 returns structure: {"Response":"Success","Data": {"Aggregated": False, "TimeFrom": ..., "TimeTo": ..., "Data":[...]}}
    if not data.get("Data") or "Data" not in data["Data"]:
        # older/other responses: check Data directly
        # attempt to parse both shapes
        if "Data" in data and isinstance(data["Data"], list):
            candles = data["Data"]
        else:
            raise RuntimeError(f"Unexpected CryptoCompare response for {symbol}: {data}")
    else:
        candles = data["Data"]["Data"]

    if not candles:
        raise RuntimeError(f"No candle data returned for {symbol}")

    df = pd.DataFrame(candles)
    # Ensure columns exist
    if "time" not in df.columns:
        raise RuntimeError(f"CryptoCompare returned unexpected structure for {symbol}: {data}")

    df = df.rename(columns={"volumefrom": "volume", "time": "timestamp"})
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    # Keep essential columns and cast
    df = df.loc[:, ["datetime", "open", "high", "low", "close", "volume"]].copy()
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    df = df.sort_values("datetime").reset_index(drop=True)
    return df

def compute_vwap_and_bands(df: pd.DataFrame, std_multiplier: float = 2.0) -> pd.DataFrame:
    """
    Compute VWAP (cumulative) and bands using rolling std of residuals.
    Returns df with columns: datetime, open, high, low, close, volume, typ, vwap, upper, lower
    """
    df = df.copy()
    # typical price
    df["typ"] = (df["high"] + df["low"] + df["close"]) / 3.0
    # cumulative sums
    df["cum_tp_vol"] = (df["typ"] * df["volume"]).cumsum()
    df["cum_vol"] = df["volume"].cumsum().replace(0, np.nan)
    df["vwap"] = df["cum_tp_vol"] / df["cum_vol"]
    df["residual"] = df["typ"] - df["vwap"]
    # rolling std of residuals - window chosen as min(20, len//5) to adapt
    window = min(20, max(1, len(df) // 5))
    df["resid_std"] = df["residual"].rolling(window=window, min_periods=1).std().fillna(0)
    df["upper"] = df["vwap"] + std_multiplier * df["resid_std"]
    df["lower"] = df["vwap"] - std_multiplier * df["resid_std"]
    return df

def compute_signal(df: pd.DataFrame) -> dict:
    """
    Compute BUY / SELL / NEUTRAL based on VWAP cross on candle close.
    Checks previous closed candle vs its VWAP and last closed candle vs its VWAP.
    Returns dict with keys: signal, reason, time
    """
    if df is None or len(df) < 2:
        return {"signal": "NEUTRAL", "reason": "not enough data", "time": None}
    prev = df.iloc[-2]
    last = df.iloc[-1]
    prev_close = prev["close"]
    prev_vwap = prev["vwap"]
    last_close = last["close"]
    last_vwap = last["vwap"]

    if (prev_close < prev_vwap) and (last_close > last_vwap):
        return {"signal": "BUY", "reason": "close crossed above VWAP", "time": last["datetime"].isoformat()}
    if (prev_close > prev_vwap) and (last_close < last_vwap):
        return {"signal": "SELL", "reason": "close crossed below VWAP", "time": last["datetime"].isoformat()}
    return {"signal": "NEUTRAL", "reason": "no cross", "time": last["datetime"].isoformat()}

# High-level wrapper to fetch and compute
def get_symbol_data(symbol: str):
    """
    Fetch candles, compute vwap/bands, compute signal.
    Returns dict: { data: [records], signal: {...} }
    In case of failure, raises or returns structured error.
    """
    try:
        df = fetch_cryptocompare_candles(symbol, aggregate_minutes=TIMEFRAME_MINUTES, limit=CANDLE_LIMIT)
    except Exception as e:
        # bubble the error with context
        raise RuntimeError(f"Error fetching candles for {symbol}: {e}")

    if df.empty:
        raise RuntimeError(f"No candles for {symbol}")

    df2 = compute_vwap_and_bands(df, std_multiplier=float(os.getenv("BAND_STD_MULTIPLIER", 2.0)))
    sig = compute_signal(df2)

    # prepare last N records for frontend (limit to 200)
    recs = []
    for _, r in df2.tail(200).iterrows():
        recs.append({
            "datetime": r["datetime"].isoformat(),
            "open": float(r["open"]),
            "high": float(r["high"]),
            "low": float(r["low"]),
            "close": float(r["close"]),
            "volume": float(r["volume"]),
            "vwap": float(r["vwap"]),
            "upper": float(r["upper"]),
            "lower": float(r["lower"]),
        })
    return {"data": recs, "signal": sig}
