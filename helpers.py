import os
import time
import math
import logging
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque

logger = logging.getLogger("helpers")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(ch)

TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")  # confere se está no Render
if not TWELVE_API_KEY:
    logger.warning("TWELVE_API_KEY não encontrado nas variáveis de ambiente.")

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
TWELVE_BASE = "https://api.twelvedata.com"

# -------------------------
# util helpers
# -------------------------
def ms_to_iso(ms):
    return datetime.fromtimestamp(ms/1000, tz=timezone.utc).isoformat()

def roundf(x, n=6):
    return None if x is None else round(float(x), n)

# Rolling VWAP: price * vol / sum(vol) over window (window in periods, default 14)
def compute_vwap(candles, window=14):
    """
    candles: list of dicts with keys: timestamp, open, high, low, close, volume
    returns list of vwap values (aligned with candles)
    """
    vwap_list = []
    pv_queue = deque()
    vol_queue = deque()
    sum_pv = 0.0
    sum_vol = 0.0

    for c in candles:
        price = (c["high"] + c["low"] + c["close"]) / 3.0 if c["high"] and c["low"] and c["close"] else c["close"]
        vol = c.get("volume", 0) or 0.0
        pv = price * vol

        pv_queue.append(pv)
        vol_queue.append(vol)
        sum_pv += pv
        sum_vol += vol

        if len(pv_queue) > window:
            sum_pv -= pv_queue.popleft()
            sum_vol -= vol_queue.popleft()

        vwap = (sum_pv / sum_vol) if sum_vol > 0 else price
        vwap_list.append(roundf(vwap, 6))

    return vwap_list

# Simple signal
def compute_signal(last_close, last_vwap, threshold_pct=0.001):
    if last_close is None or last_vwap is None:
        return "HOLD"
    diff = (last_close - last_vwap) / last_vwap
    if diff > threshold_pct:
        return "BUY"
    if diff < -threshold_pct:
        return "SELL"
    return "HOLD"

# -------------------------
# CoinGecko: build candles from market_chart (prices & volumes)
# -------------------------
def fetch_coingecko_market_chart(coin_id, vs_currency="usd", days=7):
    """
    Returns dict with 'prices' and 'total_volumes' lists.
    """
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    headers = {"accept": "application/json", "User-Agent": "VWAP-Monitor/1.0"}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()

def build_candles_from_coingecko(symbol, interval_minutes=60, days=7):
    """
    symbol: "BTCUSDT" or "ETHUSDT"
    interval_minutes: 60 for 1h candles
    returns list of candles: {timestamp_ms, open, high, low, close, volume}
    """
    mapping = {"BTCUSDT": "bitcoin", "ETHUSDT": "ethereum"}
    coin = mapping.get(symbol)
    if not coin:
        return {"error": "Coin não mapeada"}

    try:
        data = fetch_coingecko_market_chart(coin, days=days)
        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])
        if not prices:
            raise ValueError("Sem prices da CoinGecko")

        # build time-buckets by floor to interval
        bucket = {}
        step = interval_minutes * 60 * 1000  # ms
        for (p_ts, p_price) in prices:
            b = (int(p_ts) // step) * step
            rec = bucket.get(b, {"open": None, "high": -math.inf, "low": math.inf, "close": None, "volume": 0.0})
            if rec["open"] is None:
                rec["open"] = p_price
            rec["high"] = max(rec["high"], p_price)
            rec["low"] = min(rec["low"], p_price)
            rec["close"] = p_price
            bucket[b] = rec

        # accumulate volume by same buckets from volumes array
        for (v_ts, v_val) in volumes:
            b = (int(v_ts) // step) * step
            if b in bucket:
                bucket[b]["volume"] = bucket[b].get("volume", 0.0) + float(v_val)

        # sort buckets
        candles = []
        for b in sorted(bucket.keys()):
            rec = bucket[b]
            if rec["open"] is None:
                continue
            candles.append({
                "timestamp": int(b),
                "timestamp_iso": ms_to_iso(b),
                "open": roundf(rec["open"]),
                "high": roundf(rec["high"]),
                "low": roundf(rec["low"]),
                "close": roundf(rec["close"]),
                "volume": roundf(rec.get("volume", 0.0))
            })
        return candles
    except Exception as e:
        logger.error(f"Erro ao buscar {symbol} no CoinGecko: {e}")
        return {"error": str(e)}

# -------------------------
# Twelve Data: time series for forex / XAU
# -------------------------
def fetch_twelvedata_timeseries(symbol, interval="1h", outputsize=500):
    """
    symbol examples: "EUR/USD" or "XAU/USD"
    Returns list of values with open/high/low/close/volume/datetime
    """
    if not TWELVE_API_KEY:
        raise RuntimeError("TWELVE_API_KEY ausente")
    params = {"symbol": symbol, "interval": interval, "outputsize": outputsize, "format": "JSON", "apikey": TWELVE_API_KEY}
    url = f"{TWELVE_BASE}/time_series"
    r = requests.get(url, params=params, timeout=12)
    r.raise_for_status()
    j = r.json()
    if "values" not in j:
        raise ValueError(j.get("message") or j)
    return j["values"]

def build_candles_from_twelvedata(symbol_name, interval="1h"):
    """
    symbol_name: "EURUSD" or "XAUUSD" — will be converted to "EUR/USD" and "XAU/USD"
    returns candles list
    """
    fmt = symbol_name
    # convert to Twelve Data symbol format
    if symbol_name == "EURUSD":
        fmt = "EUR/USD"
    elif symbol_name == "XAUUSD":
        fmt = "XAU/USD"
    else:
        fmt = symbol_name

    try:
        values = fetch_twelvedata_timeseries(fmt, interval=interval, outputsize=500)
        candles = []
        for v in reversed(values):  # API returns newest first; normalize oldest->newest
            # v is dict with datetime, open, high, low, close, volume
            dt = v.get("datetime")
            # convert datetime to ms
            dt_obj = datetime.fromisoformat(dt).replace(tzinfo=timezone.utc)
            ts_ms = int(dt_obj.timestamp() * 1000)
            candles.append({
                "timestamp": ts_ms,
                "timestamp_iso": dt_obj.isoformat(),
                "open": roundf(v.get("open")),
                "high": roundf(v.get("high")),
                "low": roundf(v.get("low")),
                "close": roundf(v.get("close")),
                "volume": roundf(float(v.get("volume", 0.0)))
            })
        return candles
    except Exception as e:
        logger.error(f"Erro ao buscar {symbol_name} na Twelve Data: {e}")
        return {"error": str(e)}

# -------------------------
# main orchestrator
# -------------------------
def get_all_data(symbols, timeframe="1h", lookback_days=7):
    """
    symbols: list like ["BTCUSDT","ETHUSDT","EURUSD","XAUUSD"]
    returns JSON serializable dict with candles, vwap, signal for each symbol
    """
    out = {}
    for sym in symbols:
        try:
            if sym in ("BTCUSDT", "ETHUSDT"):
                # use CoinGecko fallback
                candles = build_candles_from_coingecko(sym, interval_minutes=60, days=lookback_days)
                if isinstance(candles, dict) and candles.get("error"):
                    out[sym] = {"error": candles["error"], "symbol": sym}
                    continue
            elif sym in ("EURUSD", "XAUUSD"):
                candles = build_candles_from_twelvedata(sym, interval=timeframe)
                if isinstance(candles, dict) and candles.get("error"):
                    out[sym] = {"error": candles["error"], "symbol": sym}
                    continue
            else:
                out[sym] = {"error": "Símbolo não suportado", "symbol": sym}
                continue

            # ensure list
            if not candles or not isinstance(candles, list):
                out[sym] = {"error": "Sem dados retornados", "symbol": sym}
                continue

            # compute VWAP (rolling 14)
            vwap_list = compute_vwap(candles, window=14)
            # attach vwap to candles
            for i, c in enumerate(candles):
                c["vwap"] = vwap_list[i] if i < len(vwap_list) else None

            # simple signal from last candle
            last_close = candles[-1]["close"] if candles else None
            last_vwap = candles[-1].get("vwap") if candles else None
            signal = compute_signal(last_close, last_vwap, threshold_pct=0.001)

            # prepare serializable output: reduce decimal noise
            out[sym] = {
                "symbol": sym,
                "candles": candles,
                "last_close": roundf(last_close),
                "last_vwap": roundf(last_vwap),
                "signal": signal
            }
        except Exception as e:
            logger.exception(f"Erro processando {sym}: {e}")
            out[sym] = {"error": str(e), "symbol": sym}
    return out
