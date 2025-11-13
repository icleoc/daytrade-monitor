import os
import requests
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("helpers")

TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")

def fetch_from_coingecko(symbol):
    """Obtém preço de criptos via CoinGecko"""
    mapping = {"BTCUSDT": "bitcoin", "ETHUSDT": "ethereum"}
    coin = mapping.get(symbol)
    if not coin:
        return None

    url = f"https://api.coingecko.com/api/v3/simple/price"
    headers = {"accept": "application/json", "User-Agent": "VWAP-Monitor"}
    params = {"ids": coin, "vs_currencies": "usd"}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if coin not in data or "usd" not in data[coin]:
            raise KeyError("Formato inesperado no retorno da CoinGecko")

        price = data[coin]["usd"]
        return {"symbol": symbol, "price": price, "signal": "HOLD", "data": []}
    except Exception as e:
        logger.error(f"Erro ao buscar {symbol} no CoinGecko: {e}")
        return {"symbol": symbol, "error": str(e)}

def fetch_from_twelvedata(symbol):
    """Obtém dados de forex e metais via Twelve Data"""
    if not TWELVE_API_KEY:
        return {"symbol": symbol, "error": "TWELVE_API_KEY ausente"}

    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=5min&apikey={TWELVE_API_KEY}&outputsize=60"
    try:
        r = requests.get(url, timeout=10).json()
        if "values" not in r:
            return {"symbol": symbol, "error": "Dados não retornados"}

        df = pd.DataFrame(r["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")

        # cálculo de VWAP e bandas
        df["typical_price"] = (df["high"].astype(float) + df["low"].astype(float) + df["close"].astype(float)) / 3
        df["vwap"] = df["typical_price"].rolling(window=14).mean()
        df["upper_band"] = df["vwap"] * 1.01
        df["lower_band"] = df["vwap"] * 0.99

        # sinal de compra/venda
        last = df.iloc[-1]
        signal = "BUY" if last["close"] < last["lower_band"] else "SELL" if last["close"] > last["upper_band"] else "HOLD"

        return {
            "symbol": symbol,
            "price": float(last["close"]),
            "signal": signal,
            "data": df.tail(30).to_dict(orient="records"),
        }
    except Exception as e:
        logger.error(f"Erro ao buscar {symbol} na Twelve Data: {e}")
        return {"symbol": symbol, "error": str(e)}

def get_data_for_symbol(symbol):
    """Seleciona origem correta"""
    if symbol in ["BTCUSDT", "ETHUSDT"]:
        return fetch_from_coingecko(symbol)
    else:
        return fetch_from_twelvedata(symbol)

def get_all_data():
    symbols = ["BTCUSDT", "ETHUSDT", "EURUSD", "XAUUSD"]
    results = []
    for s in symbols:
        results.append(get_data_for_symbol(s))
    return results
