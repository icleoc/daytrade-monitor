# monitor/monitor_vwap_real.py
import os
from monitor.data_fetchers import (
    fetch_binance_ohlcv,
    fetch_twelvedata_ohlcv,
    fetch_yahoo_quote,
    fetch_hgbrasil_price,
    set_twelvedata_key,
    set_hgbrasil_key
)
from utils.helpers import calc_vwap_from_ohlcv

TWELVE_KEY = os.environ.get("TWELVEDATA_API_KEY")
if TWELVE_KEY:
    set_twelvedata_key(TWELVE_KEY)

HG_KEY = os.environ.get("HG_BRASIL_API_KEY")
if HG_KEY:
    set_hgbrasil_key(HG_KEY)

ASSETS = [
    ("BTCUSD", "binance", "BTCUSDT", "1m"),
    ("ETHUSD", "binance", "ETHUSDT", "1m"),
    ("XAUUSD", "twelvedata", "XAUUSD", "5min"),
    ("EURUSD", "twelvedata", "EURUSD", "5min"),
    ("WINZ25", "hgbrasil", "WINZ25.SA", "1m"),
]

def get_asset_vwap(asset_tuple):
    label, source, src_sym, tf = asset_tuple
    try:
        if source == "binance":
            ohlcv = fetch_binance_ohlcv(src_sym, interval=tf, limit=200)
            price = ohlcv[-1]["close"]
        elif source == "twelvedata":
            ohlcv = fetch_twelvedata_ohlcv(src_sym, interval=tf, outputsize=200)
            price = ohlcv[-1]["close"]
        elif source == "hgbrasil":
            price = fetch_hgbrasil_price(src_sym)
            ohlcv = None
        else:
            return {"symbol": label, "error": "unknown source"}

        if ohlcv:
            vwap = calc_vwap_from_ohlcv(ohlcv)
        else:
            vwap = price

        signal = "NEUTRAL"
        if price and vwap:
            if price > vwap * 1.0005:
                signal = "BUY"
            elif price < vwap * 0.9995:
                signal = "SELL"

        return {
            "symbol": label,
            "price": round(price, 4),
            "vwap": round(vwap, 4),
            "signal": signal,
            "timeframe": tf
        }
    except Exception as ex:
        return {"symbol": label, "error": str(ex)}

def get_all_vwap_data():
    results = []
    for a in ASSETS:
        results.append(get_asset_vwap(a))
    return results
