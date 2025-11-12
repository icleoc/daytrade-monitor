import requests
import os
import logging

# Endpoints
BINANCE_URL = "https://api.binance.us/api/v3/klines"
TWELVE_URL = "https://api.twelvedata.com/time_series"
TWELVE_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

# Log básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_symbol_data(symbol: str, timeframe: str):
    """
    Obtém dados de candles, priorizando Binance e caindo para Twelve Data se necessário.
    """
    try:
        logger.info(f"🔹 Buscando {symbol} ({timeframe}) na Binance...")
        return get_from_binance(symbol, timeframe)
    except Exception as e:
        logger.warning(f"⚠️ Binance falhou ({e}), tentando Twelve Data...")
        return get_from_twelvedata(symbol, timeframe)

def get_from_binance(symbol: str, timeframe: str):
    """
    Busca candles de criptomoedas na Binance.
    """
    params = {
        "symbol": symbol,
        "interval": timeframe,
        "limit": 100
    }

    response = requests.get(BINANCE_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    candles = []

    for c in data:
        candles.append({
            "time": c[0],
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5]),
        })

    logger.info(f"✅ Binance retornou {len(candles)} candles para {symbol}")
    return candles

def get_from_twelvedata(symbol: str, interval: str):
    """
    Busca candles na Twelve Data (fallback).
    """
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": TWELVE_API_KEY,
        "outputsize": 100
    }

    response = requests.get(TWELVE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if "values" not in data:
        raise ValueError(f"Twelve Data retornou erro: {data}")

    candles = []
    for c in data["values"]:
        candles.append({
            "time": c["datetime"],
            "open": float(c["open"]),
            "high": float(c["high"]),
            "low": float(c["low"]),
            "close": float(c["close"]),
            "volume": float(c.get("volume", 0)),
        })

    logger.info(f"✅ Twelve Data retornou {len(candles)} candles para {symbol}")
    return candles
