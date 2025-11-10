# monitor/monitor_vwap_real.py
import time
import os
import json
import math
import requests
import datetime as dt

# yfinance para WINZ25
import yfinance as yf

CACHE_DIR = os.environ.get("CACHE_DIR", "/tmp/vwap_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

TWELVEDATA_KEY = os.environ.get("TWELVEDATA_KEY", "").strip()

COINBASE_API = "https://api.exchange.coinbase.com"  # public endpoints

# ativos configurados (símbolos "padrão" que vamos usar)
ASSETS = {
    "BTCUSD": {"type": "crypto", "product_id": "BTC-USD"},
    "ETHUSD": {"type": "crypto", "product_id": "ETH-USD"},
    "XAUUSD": {"type": "fx_gold", "td_symbol": "XAU/USD"},
    "EURUSD": {"type": "fx", "td_symbol": "EUR/USD"},
    "WINZ25": {"type": "b3", "yf_symbol": "WINZ25.SA"},
}

# helper: simple file cache (minutes)
def read_cache(key, max_age_seconds=60):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    try:
        mtime = os.path.getmtime(path)
        if time.time() - mtime > max_age_seconds:
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def write_cache(key, data):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

# VWAP calculator given OHLCV list: each element [timestamp, open, high, low, close, volume]
def calc_vwap_from_ohlcv(ohlcv):
    # expect list of dicts: {'time':..., 'price':..., 'volume':...} or candle tuples
    try:
        cumulative_vp = 0.0
        cumulative_vol = 0.0
        for c in ohlcv:
            # normalize possible shapes
            if isinstance(c, (list, tuple)) and len(c) >= 5:
                # Coinbase returns [time, low, high, open, close, volume] maybe different per API
                # We'll try to use close and volume when available
                # Prefer structure: [time, open, high, low, close, volume] OR Coinbase: [time, low, high, open, close, volume]
                # We'll try to detect which is close index
                if len(c) >= 6:
                    close = float(c[4])
                    vol = float(c[5])
                else:
                    close = float(c[1])
                    vol = float(c[2])
            elif isinstance(c, dict):
                close = float(c.get("close") or c.get("price") or c.get("c") or c.get("y") or 0)
                vol = float(c.get("volume") or c.get("v") or 0)
            else:
                continue
            cumulative_vp += close * vol
            cumulative_vol += vol
        return round((cumulative_vp / cumulative_vol), 6) if cumulative_vol > 0 else None
    except Exception:
        return None

# Fetch candles from Coinbase (public)
def fetch_coinbase_candles(product_id="BTC-USD", granularity=60, limit=200):
    # granularity in seconds (60 = 1m)
    url = f"{COINBASE_API}/products/{product_id}/candles"
    params = {"granularity": granularity, "limit": limit}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    # Coinbase returns list of [time, low, high, open, close, volume]
    return data

# Fetch from TwelveData (for XAU/USD, EUR/USD)
def fetch_twelvedata_timeseries(symbol, interval="1min", outputsize=200):
    if not TWELVEDATA_KEY:
        raise RuntimeError("TwelveData key not configured in TWELVEDATA_KEY environment variable.")
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "format": "JSON",
        "apikey": TWELVEDATA_KEY,
    }
    r = requests.get(url, params=params, timeout=12)
    data = r.json()
    if "status" in data and data.get("status") == "error":
        raise RuntimeError(f"TwelveData error: {data}")
    # convert to list of dicts with close, volume
    values = data.get("values") or []
    ohlcv = []
    for v in values:
        ohlcv.append({
            "time": v.get("datetime") or v.get("timestamp"),
            "open": float(v.get("open", 0)),
            "high": float(v.get("high", 0)),
            "low": float(v.get("low", 0)),
            "close": float(v.get("close", 0)),
            "volume": float(v.get("volume", 0) or 0)
        })
    return ohlcv

# fetch WINZ25 via yfinance (delayed)
def fetch_win_via_yf(symbol="WINZ25.SA", interval="1m", period="1d"):
    # yfinance uses period and interval strings
    df = yf.download(tickers=symbol, interval=interval, period=period, progress=False)
    if df is None or df.empty:
        raise RuntimeError(f"HG Brasil no data for {symbol}")
    ohlcv = []
    for idx, row in df.iterrows():
        close = float(row["Close"])
        vol = float(row.get("Volume", 0) or 0)
        ohlcv.append({"time": str(idx), "close": close, "volume": vol})
    return ohlcv

def get_vwap_for_asset(key):
    a = ASSETS.get(key)
    if not a:
        return {"error": "unknown asset"}
    cache_key = f"vwap_{key}"
    cached = read_cache(cache_key, max_age_seconds=30)
    if cached:
        return cached
    try:
        if a["type"] == "crypto":
            candles = fetch_coinbase_candles(product_id=a["product_id"], granularity=60, limit=200)
            vwap = calc_vwap_from_ohlcv(candles)
        elif a["type"] in ("fx", "fx_gold"):
            # TwelveData symbol uses XAU/USD or EUR/USD format
            td_sym = a["td_symbol"]
            ohlcv = fetch_twelvedata_timeseries(td_sym, interval="1min", outputsize=200)
            vwap = calc_vwap_from_ohlcv(ohlcv)
        elif a["type"] == "b3":
            ohlcv = fetch_win_via_yf(a["yf_symbol"], interval="1m", period="1d")
            vwap = calc_vwap_from_ohlcv(ohlcv)
        else:
            vwap = None
        result = {"asset": key, "vwap": vwap, "ts": dt.datetime.utcnow().isoformat() + "Z"}
        write_cache(cache_key, result)
        return result
    except Exception as e:
        # fallback to cache if exists
        last = read_cache(cache_key, max_age_seconds=3600)
        if last:
            return {"asset": key, "vwap": last.get("vwap"), "warning": f"error fetching fresh data: {str(e)}"}
        return {"asset": key, "error": str(e)}

def get_all_vwap_data():
    out = {}
    for key in ASSETS.keys():
        out[key] = get_vwap_for_asset(key)
        # small sleep to avoid bursting external APIs
        time.sleep(0.6)
    return out

if __name__ == "__main__":
    print(json.dumps(get_all_vwap_data(), indent=2))
