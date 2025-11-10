# monitor/monitor_vwap_real.py
import os
from monitor.data_fetchers import (
    fetch_binance_ohlcv,
    fetch_twelvedata_ohlcv,
    fetch_yahoo_quote,
    set_twelvedata_key
)
from utils.helpers import calc_vwap_from_ohlcv

# configurar key
TWELVE_KEY = os.environ.get("TWELVEDATA_API_KEY") or os.environ.get("TWELVE_API_KEY")
if TWELVE_KEY:
    set_twelvedata_key(TWELVE_KEY)

# Ativos que queremos (mantive a lista que você definiu no início)
ASSETS = [
    # symbol, source, exchange-specific symbol, timeframe
    ("BTCUSD", "binance", "BTCUSDT", "1m"),
    ("ETHUSD", "binance", "ETHUSDT", "1m"),
    ("XAUUSD", "twelvedata", "XAUUSD", "5min"),
    ("EURUSD", "twelvedata", "EURUSD", "5min"),
    ("WINZ25", "yahoo", "WINZ25.SA", "1m"),  # fallback para WIN
]

def get_asset_vwap(symbol_tuple):
    label, source, src_sym, tf = symbol_tuple
    try:
        if source == "binance":
            ohlcv = fetch_binance_ohlcv(src_sym, interval=tf, limit=200)
        elif source == "twelvedata":
            ohlcv = fetch_twelvedata_ohlcv(src_sym, interval=tf, outputsize=200)
        elif source == "yahoo":
            # yahoo fallback: try quote -> not candles (use last price)
            q = fetch_yahoo_quote(src_sym)
            # build a synthetic single-candle list:
            ohlcv = [{"t": q.get("timestamp") or 0, "open": q["price"], "high": q["price"],
                      "low": q["price"], "close": q["price"], "volume": 0}]
        else:
            return {"symbol": label, "error": "unknown source"}

        vwap = calc_vwap_from_ohlcv(ohlcv)
        last_price = ohlcv[-1]["close"] if ohlcv else None

        # SINAL: definição simples — preço > vwap => 'BUY', price < vwap => 'SELL', else 'NEUTRAL'
        signal = "NEUTRAL"
        if last_price is not None and vwap is not None:
            if last_price > vwap * 1.0005:
                signal = "BUY"
            elif last_price < vwap * 0.9995:
                signal = "SELL"

        return {
            "symbol": label,
            "source": source,
            "price": float(last_price) if last_price is not None else None,
            "vwap": float(vwap) if vwap is not None else None,
            "signal": signal,
            "timeframe": tf
        }
    except Exception as e:
        return {"symbol": label, "error": str(e)}

def get_all_vwap_data():
    results = []
    for s in ASSETS:
        results.append(get_asset_vwap(s))
    return results
