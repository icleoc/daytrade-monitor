import os
import requests
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")

def fetch_coingecko(symbol):
    """Busca preço e VWAP básico para BTC e ETH usando CoinGecko"""
    url_map = {
        "BTCUSDT": "bitcoin",
        "ETHUSDT": "ethereum"
    }

    if symbol not in url_map:
        return {"symbol": symbol, "error": "Símbolo não suportado pela CoinGecko"}

    coin = url_map[symbol]
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=3&interval=hourly"

    try:
        logger.info(f"🔹 Buscando {symbol} (CoinGecko)...")
        resp = requests.get(url, timeout=10)
        data = resp.json()
        prices = data.get("prices", [])
        if not prices:
            raise ValueError("Sem dados retornados")

        df = pd.DataFrame(prices, columns=["timestamp", "close"])
        df["close"] = df["close"].astype(float)
        df["vwap"] = df["close"].rolling(10).mean()

        return {
            "symbol": symbol,
            "price": round(df["close"].iloc[-1], 2),
            "vwap": round(df["vwap"].iloc[-1], 2),
            "source": "CoinGecko"
        }

    except Exception as e:
        logger.error(f"❌ Erro ao buscar {symbol} no CoinGecko: {e}")
        return {"symbol": symbol, "error": str(e)}


def fetch_twelvedata(symbol):
    """Busca preço e VWAP de EURUSD e XAUUSD no Twelve Data"""
    if not TWELVE_API_KEY:
        return {"symbol": symbol, "error": "TWELVE_API_KEY ausente"}

    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1h&outputsize=100&apikey={TWELVE_API_KEY}"

    try:
        logger.info(f"🔹 Buscando {symbol} (Twelve Data)...")
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if "values" not in data:
            raise ValueError(data.get("message", "Erro desconhecido"))

        df = pd.DataFrame(data["values"])
        df["close"] = df["close"].astype(float)
        df["vwap"] = df["close"].rolling(10).mean()

        return {
            "symbol": symbol,
            "price": round(df["close"].iloc[0], 4),
            "vwap": round(df["vwap"].iloc[0], 4),
            "source": "Twelve Data"
        }

    except Exception as e:
        logger.error(f"❌ Erro ao buscar {symbol} na Twelve Data: {e}")
        return {"symbol": symbol, "error": str(e)}


def get_all_assets_data():
    """Busca dados de todos os ativos configurados"""
    assets = ["BTCUSDT", "ETHUSDT", "EURUSD", "XAUUSD"]
    results = {}

    for asset in assets:
        if asset in ["BTCUSDT", "ETHUSDT"]:
            results[asset] = fetch_coingecko(asset)
        else:
            results[asset] = fetch_twelvedata(asset)

    return results
