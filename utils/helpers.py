# helpers.py
import time
import math
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from config import CRYPTOCOMPARE_API_KEY, CRYPTOCOMPARE_BASE, TIMEFRAME_MINUTES, CANDLE_LIMIT

HEADERS = {"authorization": f"Apikey {CRYPTOCOMPARE_API_KEY}"} if CRYPTOCOMPARE_API_KEY else {}

def fetch_crypto_compare_histo(symbol, quote="USD", aggregate_minutes=15, limit=200):
    """
    Busca candles 15m (ou o aggregate especificado) da CryptoCompare.
    Retorna DataFrame com columns: time, open, high, low, close, volumefrom, volumeto
    """
    # endpoint histominute com aggregate
    url = f"{CRYPTOCOMPARE_BASE}/v2/histominute"
    params = {
        "fsym": symbol,
        "tsym": quote,
        "aggregate": aggregate_minutes,
        "limit": limit - 1,
        "e": "CCCAGG"
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if data.get("Response", "").lower() == "error":
        raise RuntimeError(data.get("Message", "Error from CryptoCompare"))
    candles = data["Data"]["Data"]
    df = pd.DataFrame(candles)
    # ensure correct columns
    df = df.rename(columns={"time": "timestamp", "volumefrom": "volume"})
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
    df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
    return df

def fetch_exchange_rate_ohlc(symbol_pair="EURUSD", aggregate_minutes=15, limit=200):
    """
    Para EURUSD e XAUUSD: tenta usar CryptoCompare first (if supported),
    otherwise fallback to a simple construction using exchange rates (coarser).
    Here we try CryptoCompare if symbol like EUR => 'EUR' + 'USD'
    """
    base, quote = symbol_pair[:3], symbol_pair[3:]
    try:
        return fetch_crypto_compare_histo(base, quote, aggregate_minutes, limit)
    except Exception:
        # fallback: use ExchangeRate.host requires building OHLC from rates snapshots
        # NOTE: ExchangeRate.host provides daily rates; for intraminute you may need a paid provider.
        # We'll raise for clarity so user can plug a provider for intraminute FX/XAU.
        raise RuntimeError("Provider for intraminute OHLC for FX/XAU not configured. Use CryptoCompare or an FX intraday API.")

def compute_vwap_and_bands(df, std_multiplier=2.0):
    """
    df: pandas DataFrame with columns datetime, open, high, low, close, volume
    Compute VWAP per-candle and rolling bands (using typical price residuals)
    Returns df with columns vwap, upper_band, lower_band
    """
    df = df.copy()
    # typical price
    df['typ'] = (df['high'] + df['low'] + df['close']) / 3.0
    # cumulative typical price * volume and cumulative volume to compute VWAP over the entire history window
    df['cum_tp_vol'] = (df['typ'] * df['volume']).cumsum()
    df['cum_vol'] = df['volume'].cumsum().replace(0, np.nan)
    df['vwap'] = df['cum_tp_vol'] / df['cum_vol']
    # residual: typ - vwap
    df['residual'] = df['typ'] - df['vwap']
    # compute rolling std of residual with a window (use 20 by default or full window)
    window = min(20, max(1, len(df)//5))
    df['resid_std'] = df['residual'].rolling(window=window, min_periods=1).std().fillna(0)
    df['upper_band'] = df['vwap'] + std_multiplier * df['resid_std']
    df['lower_band'] = df['vwap'] - std_multiplier * df['resid_std']
    return df

def compute_signal(df, rule=None):
    """
    Compute buy/sell/neutral signal for the latest (most recent closed) candle.
    rule: dict from config.SIGNAL_RULE
    Returns dict: {"signal": "BUY"|"SELL"|"NEUTRAL", "reason": "...", "time": datetime}
    """
    if rule is None:
        rule = {}
    rows = df.reset_index(drop=True)
    if len(rows) < 2:
        return {"signal": "NEUTRAL", "reason": "not enough data", "time": rows['datetime'].iloc[-1] if len(rows) else None}

    last = rows.iloc[-1]
    prev = rows.iloc[-2]

    # default cross-based rule
    if rule.get("use_vwap_cross", True):
        # previous close vs prev vwap, last close vs last vwap
        prev_close = prev['close']
        prev_vwap = prev['vwap']
        last_close = last['close']
        last_vwap = last['vwap']

        # cross up -> BUY, cross down -> SELL
        if (prev_close < prev_vwap) and (last_close > last_vwap):
            return {"signal": "BUY", "reason": "close crossed above VWAP", "time": last['datetime']}
        if (prev_close > prev_vwap) and (last_close < last_vwap):
            return {"signal": "SELL", "reason": "close crossed below VWAP", "time": last['datetime']}

    return {"signal": "NEUTRAL", "reason": "no cross detected", "time": last['datetime']}
