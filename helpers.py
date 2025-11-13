import requests
import time
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("helpers")

API_KEY = "TwelveData_API_Key_Aqui"  # já configurado no Render
TWELVE_URL = "https://api.twelvedata.com/time_series"

# Dicionário com símbolos e nomes compatíveis
SYMBOL_MAP = {
    "BTCUSDT": "BTC/USD",
    "ETHUSDT": "ETH/USD",
    "EURUSD": "EUR/USD",
    "XAUUSD": "XAU/USD"
}

CACHE = {}
LAST_FETCH = {}

def fetch_twelve(symbol):
    """Busca candles reais e calcula VWAP"""
    now = time.time()
    if symbol in CACHE and now - LAST_FETCH.get(symbol, 0) < 60:
        return CACHE[symbol]

    try:
        params = {
            "symbol": SYMBOL_MAP[symbol],
            "interval": "15min",
            "apikey": API_KEY,
            "outputsize": 50
        }
        r = requests.get(TWELVE_URL, params=params, timeout=10)
        data = r.json()
        values = data.get("values", [])
        if not values:
            raise Exception("Dados não retornados")

        # Converter para float e inverter ordem (mais antigo primeiro)
        candles = [{
            "datetime": v["datetime"],
            "open": float(v["open"]),
            "high": float(v["high"]),
            "low": float(v["low"]),
            "close": float(v["close"]),
            "volume": float(v.get("volume", 0))
        } for v in reversed(values)]

        # VWAP = (Σ (Preço Médio * Volume)) / Σ Volume
        total_pv = 0
        total_vol = 0
        for c in candles:
            price_mean = (c["high"] + c["low"] + c["close"]) / 3
            vol = c["volume"] if c["volume"] > 0 else 1
            total_pv += price_mean * vol
            total_vol += vol
        vwap = total_pv / total_vol if total_vol else candles[-1]["close"]

        latest = candles[-1]["close"]
        CACHE[symbol] = {"price": latest, "vwap": vwap, "candles": candles}
        LAST_FETCH[symbol] = now
        return CACHE[symbol]
    except Exception as e:
        logger.error(f"Erro ao buscar {symbol}: {e}")
        return {"error": str(e)}

def get_all_data():
    data = {}
    for symbol in SYMBOL_MAP:
        data[symbol] = fetch_twelve(symbol)
    return data
