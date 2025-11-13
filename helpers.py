import time
import requests
import logging
import math
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from config import TWELVE_API_KEY, BAND_STD_MULTIPLIER, MAX_CANDLES

logger = logging.getLogger("helpers")
logger.setLevel(logging.INFO)

# in-memory cache: { symbol: { 'ts': epoch_seconds, 'data': result_dict } }
_CACHE = {}

# mapping our project symbols to Twelve Data symbol names (when needed)
TWELVE_SYMBOL_MAP = {
    "BTCUSDT": "BTC/USD",
    "ETHUSDT": "ETH/USD",
    "EURUSD": "EUR/USD",
    "XAUUSD": "XAU/USD"
}

def _cache_get(symbol):
    entry = _CACHE.get(symbol)
    if not entry:
        return None
    if time.time() - entry["ts"] > 60:  # 60s TTL (config.UPDATE_INTERVAL_SECONDS)
        return None
    return entry["data"]

def _cache_set(symbol, data):
    _CACHE[symbol] = {"ts": time.time(), "data": data}

def _ts_to_iso(ts):
    # ts in milliseconds or seconds
    if ts > 1e12:
        # milliseconds
        ts = int(ts/1000)
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()

def compute_vwap_and_bands(df):
    """
    df: DataFrame with columns: open, high, low, close, volume, index=timestamp (ms or datetime)
    returns df with vwap, upper, lower
    """
    df = df.copy()
    # ensure numeric
    for c in ["open","high","low","close","volume"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)

    # typical price
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    cum_tp_vol = (tp * df["volume"]).cumsum()
    cum_vol = df["volume"].cumsum()
    # avoid div by zero
    vwap = cum_tp_vol / cum_vol.replace(0, np.nan)
    vwap = vwap.fillna(method="ffill").fillna(df["close"])

    df["vwap"] = vwap

    # bands as vwap +/- std(tp) * multiplier (rolling std)
    rolling_std = tp.rolling(window=20, min_periods=1).std().fillna(0)
    df["upper"] = df["vwap"] + (rolling_std * BAND_STD_MULTIPLIER)
    df["lower"] = df["vwap"] - (rolling_std * BAND_STD_MULTIPLIER)
    return df

def decide_signals(df):
    """
    Simple strategy:
    - last close > last upper => SELL
    - last close < last lower => BUY
    - else HOLD
    Also annotate all candles where price crossed bands (for plotting)
    """
    df = df.copy()
    df["signal"] = "HOLD"
    # crossover detections per candle
    df.loc[df["close"] > df["upper"], "signal"] = "SELL"
    df.loc[df["close"] < df["lower"], "signal"] = "BUY"
    # create annotated points: for each candle that is BUY/SELL return index and label
    signals = []
    for idx, row in df.iterrows():
        if row["signal"] in ("BUY", "SELL"):
            signals.append({
                "time": _ts_to_iso(idx) if isinstance(idx, (int, float)) else _ts_to_iso(int(pd.Timestamp(idx).timestamp()*1000)),
                "price": float(row["close"]),
                "type": row["signal"]
            })
    # summary current signal
    current = df.iloc[-1]["signal"] if len(df) > 0 else "HOLD"
    return df, signals, current

def _twelvedata_time_series(symbol, interval="15m", outputsize=100):
    if not TWELVE_API_KEY:
        raise RuntimeError("TWELVE_API_KEY ausente")
    url = "https://api.twelvedata.com/time_series"
    mapped = TWELVE_SYMBOL_MAP.get(symbol, symbol)
    params = {
        "symbol": mapped,
        "interval": interval,
        "apikey": TWELVE_API_KEY,
        "outputsize": outputsize,
        "format": "JSON"
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if "values" not in data:
        raise RuntimeError(data.get("message") or str(data))
    values = data["values"]  # list with newest first
    # convert to DataFrame oldest -> newest
    df = pd.DataFrame(values)[["datetime","open","high","low","close","volume"]]
    df = df.iloc[::-1].reset_index(drop=True)
    # convert index to timestamp ms
    # twelve returns datetime strings like '2025-11-12 21:00:00'
    df.index = (pd.to_datetime(df["datetime"]).astype(int) // 10**6).astype(int)
    df = df.drop(columns=["datetime"])
    # ensure types
    df = df.astype({"open":"float","high":"float","low":"float","close":"float","volume":"float"})
    return df

def _coingecko_market_chart(symbol, days=1, interval_minutes=15):
    """
    symbol: 'BTCUSDT' or 'ETHUSDT' expected -> map to coin id
    Returns DataFrame indexed by timestamp(ms) with open/high/low/close/volume
    NOTE: CoinGecko market_chart returns prices and total_volumes arrays.
    We will convert prices to OHLC by grouping per interval_minutes.
    """
    # map
    coin_map = {"BTCUSDT":"bitcoin", "ETHUSDT":"ethereum"}
    coin = coin_map.get(symbol)
    if not coin:
        raise RuntimeError("CoinGecko fallback não suporta: " + symbol)
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {"vs_currency":"usd", "days": days, "interval": "minute"}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    prices = data.get("prices", [])
    volumes = data.get("total_volumes", [])
    if not prices:
        raise RuntimeError("Sem dados retornados")
    # create DataFrame with ms timestamp
    p_df = pd.DataFrame(prices, columns=["ts","price"])
    v_df = pd.DataFrame(volumes, columns=["ts","volume"])
    df = p_df.merge(v_df, on="ts", how="left")
    # convert to pandas datetime and resample to interval_minutes
    df["datetime"] = pd.to_datetime(df["ts"], unit="ms")
    df = df.set_index("datetime")
    ohlc = df["price"].resample(f"{interval_minutes}T").ohlc()
    vol = df["volume"].resample(f"{interval_minutes}T").sum().fillna(0)
    combined = pd.concat([ohlc, vol], axis=1).dropna(subset=["close"])
    # set index to epoch ms
    combined.index = (combined.index.astype(int) // 10**6).astype(int)
    combined = combined.rename(columns={"sum":"volume"})
    combined = combined.rename(columns={0:"ignore"}) if "ignore" in combined.columns else combined
    combined = combined.rename(columns={"volume":"volume"})
    combined = combined[["open","high","low","close","volume"]]
    return combined

def fetch_symbol_data(symbol, interval="15m", limit=100):
    """
    Returns dict:
    {
      timestamps: [... ISO ...],
      open: [...],
      high: [...],
      low: [...],
      close: [...],
      volume: [...],
      vwap: [...],
      upper: [...],
      lower: [...],
      signals: [{time, price, type}],
      summary: { symbol, last_price, last_signal }
    }
    """
    # cache check
    cached = _cache_get(symbol)
    if cached:
        return cached

    df = None
    error = None
    try:
        # Prefer Twelve Data
        if TWELVE_API_KEY:
            logger.info(f"🔹 Buscando {symbol} na Twelve Data...")
            df = _twelvedata_time_series(symbol, interval=interval, outputsize=limit)
        else:
            raise RuntimeError("TWELVE_API_KEY ausente")
    except Exception as e:
        logger.warning(f"⚠️ Falha Twelve Data para {symbol}: {e}")
        error = str(e)
        # fallback for crypto to CoinGecko
        if symbol in ("BTCUSDT", "ETHUSDT"):
            try:
                logger.info(f"🔹 Tentando fallback CoinGecko para {symbol}...")
                df = _coingecko_market_chart(symbol, days=7, interval_minutes=15)
            except Exception as e2:
                logger.error(f"❌ Erro CoinGecko para {symbol}: {e2}")
                error = f"{error} | fallback_coin_gecko:{e2}"
        # else, keep error
    if df is None:
        result = {"error": error or "Sem dados"}
        _cache_set(symbol, result)
        return result

    # limit rows
    if len(df) > limit:
        df = df.iloc[-limit:]

    # compute vwap and bands
    try:
        df2 = compute_vwap_and_bands(df)
        df2, signals, current_signal = decide_signals(df2)
    except Exception as e:
        logger.exception("Erro ao calcular VWAP/bandas/sinais")
        result = {"error": "Erro calculando indicadores: " + str(e)}
        _cache_set(symbol, result)
        return result

    # prepare arrays
    timestamps = []
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    vwaps = []
    uppers = []
    lowers = []

    for idx, row in df2.iterrows():
        # idx is epoch ms (int)
        if isinstance(idx, (int, float)):
            iso = _ts_to_iso(idx)
        else:
            # fallback
            iso = _ts_to_iso(int(pd.Timestamp(idx).timestamp()*1000))
        timestamps.append(iso)
        opens.append(float(row["open"]))
        highs.append(float(row["high"]))
        lows.append(float(row["low"]))
        closes.append(float(row["close"]))
        volumes.append(float(row["volume"]))
        vwaps.append(float(row["vwap"]))
        uppers.append(float(row["upper"]))
        lowers.append(float(row["lower"]))

    summary = {
        "symbol": symbol,
        "last_price": closes[-1] if len(closes) else None,
        "last_signal": current_signal
    }

    result = {
        "symbol": symbol,
        "timestamps": timestamps,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
        "vwap": vwaps,
        "upper": uppers,
        "lower": lowers,
        "signals": signals,
        "summary": summary
    }

    _cache_set(symbol, result)
    return result

def get_all_data(symbols=None, interval="15m", limit=100):
    symbols = symbols or []
    out = {}
    for s in symbols:
        try:
            out[s] = fetch_symbol_data(s, interval=interval, limit=limit)
        except Exception as e:
            logger.exception("Erro geral")
            out[s] = {"error": str(e), "symbol": s}
    return out
