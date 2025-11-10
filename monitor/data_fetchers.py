# monitor/data_fetchers.py
import requests
import time
from typing import Optional, Dict, Any

TWELVEDATA_API_KEY = None  # será lido das env vars pelo monitor principal

def set_twelvedata_key(key: str):
    global TWELVEDATA_API_KEY
    TWELVEDATA_API_KEY = key

# ---------- Binance (candles/public) ----------
def fetch_binance_ohlcv(symbol: str, interval: str = "1m", limit: int = 200):
    """
    symbol: ex: 'BTCUSDT' ou 'ETHUSDT'
    interval: Binance interval string (1m, 5m, ...)
    """
    base = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(base, params=params, timeout=10)
    r.raise_for_status()
    # Response: list of lists. returns list of dicts (open,time,high,low,close,volume)
    data = []
    for k in r.json():
        data.append({
            "t": int(k[0]) // 1000,
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5])
        })
    return data

# ---------- Twelve Data (time series) ----------
def fetch_twelvedata_ohlcv(symbol: str, interval: str = "5min", outputsize: int = 200):
    """
    symbol: ex: 'EURUSD' or 'XAUUSD'
    interval: 1min, 5min, 15min, 1h, etc (twelvedata accepts '5min')
    requires TWELVEDATA_API_KEY set via set_twelvedata_key or env var
    """
    if not TWELVEDATA_API_KEY:
        raise RuntimeError("Twelve Data API key not set.")
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
    # handle errors
    if "values" not in j:
        raise RuntimeError(f"TwelveData error: {j}")
    # values come newest first or oldest? they usually come most recent first -> reverse to oldest->newest
    values = list(reversed(j["values"]))
    data = []
    for v in values:
        data.append({
            "t": int(time.mktime(time.strptime(v["datetime"], "%Y-%m-%d %H:%M:%S"))),
            "open": float(v["open"]),
            "high": float(v["high"]),
            "low": float(v["low"]),
            "close": float(v["close"]),
            "volume": float(v.get("volume", 0) or 0)
        })
    return data

# ---------- Yahoo Finance (quote fallback for WIN / simple price) ----------
def fetch_yahoo_quote(symbol: str) -> Dict[str, Any]:
    """
    symbol examples:
      - BTC-USD
      - ETH-USD
      - EURUSD=X
      - XAUUSD=X
      - ^BVSP  (IBOV)
    For WIN mini index, there isn't a guaranteed standardized symbol on Yahoo for futures;
    try variations (e.g. WINZ25.SA). This is a best-effort fallback.
    """
    base = "https://query1.finance.yahoo.com/v7/finance/quote"
    params = {"symbols": symbol}
    r = requests.get(base, params=params, timeout=8)
    r.raise_for_status()
    j = r.json()
    if not j.get("quoteResponse") or not j["quoteResponse"].get("result"):
        raise RuntimeError("Yahoo returned no result.")
    res = j["quoteResponse"]["result"][0]
    return {
        "symbol": res.get("symbol"),
        "price": res.get("regularMarketPrice"),
        "timestamp": res.get("regularMarketTime"),
        "raw": res
    }
