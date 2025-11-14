import os
import logging
import requests

logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv("TWELVE_API_KEY")
BASE_URL = "https://api.twelvedata.com/time_series"


def fetch_symbol_data(symbol: str, interval: str = "15min"):
    """
    Busca OHLCV diretamente da API TwelveData via HTTP.
    """
    try:
        logging.info(f"Buscando dados para {symbol} ({interval})...")

        params = {
            "symbol": symbol,
            "interval": interval,
            "apikey": API_KEY,
            "outputsize": 1
        }

        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if "values" not in data:
            raise ValueError(f"Erro retorno API: {data}")

        latest = data["values"][0]

        return {
            "symbol": symbol,
            "open": float(latest["open"]),
            "high": float(latest["high"]),
            "low": float(latest["low"]),
            "close": float(latest["close"]),
            "volume": float(latest.get("volume", 0)),
        }

    except Exception as e:
        logging.error(f"Erro ao buscar {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}


def get_all_symbols_data(symbols):
    """
    Retorna dados de múltiplos símbolos.
    """
    results = []
    for s in symbols:
        results.append(fetch_symbol_data(s))
    return results


def normalize_symbol(symbol: str):
    mapping = {
        "BTC/USDT": "Bitcoin",
        "ETH/USDT": "Ethereum",
        "EUR/USD": "Euro x Dólar",
        "XAU/USD": "Ouro"
    }
    return mapping.get(symbol, symbol)
