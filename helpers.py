import requests
import time
import logging
import os

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("helpers")

API_KEY = os.getenv("TWELVE_API_KEY")  # vem do Render
TWELVE_URL = "https://api.twelvedata.com/time_series"

SYMBOL_MAP = {
    "BTCUSDT": "BTC/USD",
    "ETHUSDT": "ETH/USD",
    "EURUSD": "EUR/USD",
    "XAUUSD": "XAU/USD"
}

CACHE = {}
LAST_FETCH = {}

def fetch_twelve(symbol):
    now = time.time()
    if symbol in CACHE and now - LAST_FETCH.get(symbol, 0) < 60:
        return CACHE[symbol]

    try:
        params = {
            "symbol": SYMBOL_MAP[symbol],
            "interval": "15min",
            "apikey": API_KEY,
            "outputsize": 80
        }
        r = requests.get(TWELVE_URL, params=params, timeout=10)
        data = r.json()
        values = data.get("values", [])
        if not values:
            raise Exception(f"Nenhum dado retornado para {symbol}")

        # Converter para floats
        candles = [{
            "datetime": v["datetime"],
            "open": float(v["open"]),
            "high": float(v["high"]),
            "low": float(v["low"]),
            "close": float(v["close"]),
            "volume": float(v.get("volume", 0) or 1)
        } for v in reversed(values)]

        # VWAP dinâmico — linha contínua
        vwap_values = []
        total_pv = 0
        total_vol = 0
        for c in candles:
            price_mean = (c["high"] + c["low"] + c["close"]) / 3
            total_pv += price_mean * c["volume"]
            total_vol += c["volume"]
            vwap_values.append(total_pv / total_vol)

        last_price = candles[-1]["close"]
        last_vwap = vwap_values[-1]

        result = {
            "price": last_price,
            "vwap": last_vwap,
            "vwap_series": vwap_values,
            "candles": candles
        }

        CACHE[symbol] = result
        LAST_FETCH[symbol] = now
        return result

    except Exception as e:
        logger.error(f"Erro ao buscar {symbol}: {e}")
        return {"error": str(e)}

def get_all_data():
    data = {}
    for s in SYMBOL_MAP:
        data[s] = fetch_twelve(s)
    return data
