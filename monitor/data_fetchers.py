# monitor/data_fetchers.py
import requests
import time
import numpy as np
import yfinance as yf
from typing import Optional, List, Dict, Any

TWELVEDATA_API_KEY = None
HG_BRASIL_API_KEY = None

def set_twelvedata_key(key: str):
    global TWELVEDATA_API_KEY
    TWELVEDATA_API_KEY = key

def set_hgbrasil_key(key: str):
    global HG_BRASIL_API_KEY
    HG_BRASIL_API_KEY = key

def fetch_binance_ohlcv(symbol: str, interval: str = "1m", limit: int = 200) -> List[Dict[str, Any]]:
    base = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(base, params=params, timeout=10)
    r.raise_for_status()
    result = []
    for k in r.json():
        result.append({
            "t": int(k[0]) // 1000,
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5])
        })
    return result

def fetch_twelvedata_ohlcv(symbol: str, interval: str = "5min", outputsize: int = 200) -> List[Dict[str, Any]]:
    if not TWELVEDATA_API_KEY:
        raise RuntimeError("TwelveData API key not set.")
    base = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "format": "json",
        "apikey": TWELVEDATA_API_KEY
    }
    r = requests.get(base, params=params, timeout=12)
    r.raise_for_status()
    j = r.json()
    if "values" not in j:
        raise RuntimeError(f"TwelveData error: {j}")
    values = list(reversed(j["values"]))
    data = []
    for v in values:
        # convert datetime string to timestamp
        ts = int(time.mktime(time.strptime(v["datetime"], "%Y-%m-%d %H:%M:%S")))
        data.append({
            "t": ts,
            "open": float(v["open"]),
            "high": float(v["high"]),
            "low": float(v["low"]),
            "close": float(v["close"]),
            "volume": float(v.get("volume", 0) or 0)
        })
    return data

def fetch_yahoo_quote(symbol: str) -> Dict[str, Any]:
    r = yf.Ticker(symbol).history(period="1d", interval="1m")
    if r.empty:
        raise RuntimeError(f"Yahoo no data for {symbol}")
    latest = r.iloc[-1]
    return {
        "symbol": symbol,
        "price": float(latest["Close"]),
        "volume": float(latest["Volume"]),
        "time": latest.name.timestamp()
    }

def fetch_hgbrasil_price(symbol: str) -> float:
    if not HG_BRASIL_API_KEY:
        raise RuntimeError("HG Brasil API key not set.")
    base = "https://api.hgbrasil.com/finance/stock_price"
    params = {"key": HG_BRASIL_API_KEY, "symbol": symbol}
    r = requests.get(base, params=params, timeout=8)
    r.raise_for_status()
    j = r.json()
    if not j.get("results", {}).get(symbol):
        raise RuntimeError(f"HG Brasil no data for {symbol}: {j}")
    return float(j["results"][symbol]["price"])
