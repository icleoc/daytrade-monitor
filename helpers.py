import requests
import time
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("helpers")

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
TWELVE_URL = "https://api.twelvedata.com/time_series"

COINGECKO_IDS = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum"
}

TWELVE_SYMBOLS = {
    "EURUSD": "EUR/USD",
    "XAUUSD": "XAU/USD"
}

CACHE = {}
LAST_FETCH = {}

API_KEY = "TwelveData_API_Key_Aqui"  # já configurado no Render

def fetch_coingecko(symbol):
    now = time.time()
    if symbol in CACHE and now - LAST_FETCH.get(symbol, 0) < 60:
        return CACHE[symbol]

    try:
        coin_id = COINGECKO_IDS[symbol]
        params = {"ids": coin_id, "vs_currencies": "usd"}
        r = requests.get(COINGECKO_URL, params=params, timeout=10)
        data = r.json()
        price = data[coin_id]["usd"]
        vwap = price * 0.995  # valor simulado de exemplo
        CACHE[symbol] = {"price": price, "vwap": vwap}
        LAST_FETCH[symbol] = now
        return CACHE[symbol]
    except Exception as e:
        logger.error(f"Erro ao buscar {symbol} no CoinGecko: {e}")
        return {"error": str(e)}

def fetch_twelve(symbol):
    now = time.time()
    if symbol in CACHE and now - LAST_FETCH.get(symbol, 0) < 60:
        return CACHE[symbol]

    try:
        r = requests.get(TWELVE_URL, params={
            "symbol": TWELVE_SYMBOLS[symbol],
            "interval": "15min",
            "apikey": API_KEY,
            "outputsize": 20
        }, timeout=10)
        data = r.json()
        values = data.get("values", [])
        if not values:
            raise Exception("Dados não retornados")
        latest = float(values[0]["close"])
        vwap = sum(float(v["close"]) for v in values) / len(values)
        CACHE[symbol] = {"price": latest, "vwap": vwap}
        LAST_FETCH[symbol] = now
        return CACHE[symbol]
    except Exception as e:
        logger.error(f"Erro ao buscar {symbol} no Twelve Data: {e}")
        return {"error": str(e)}

def get_all_data():
    data = {}
    for symbol in ["BTCUSDT", "ETHUSDT"]:
        data[symbol] = fetch_coingecko(symbol)
    for symbol in ["EURUSD", "XAUUSD"]:
        data[symbol] = fetch_twelve(symbol)
    return data
