import os
import requests
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")

# ---------------------------------------------------------
# 🔹 CoinGecko: busca de preço direto (rápido e confiável)
# ---------------------------------------------------------
def fetch_coingecko(symbol):
    url_map = {
        "BTCUSDT": "bitcoin",
        "ETHUSDT": "ethereum"
    }

    if symbol not in url_map:
        return {"symbol": symbol, "error": "Símbolo não suportado pela CoinGecko"}

    coin = url_map[symbol]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"

    try:
        logger.info(f"🔹 Buscando {symbol} (CoinGecko)...")
        resp = requests.get(url, timeout=10)
        data = resp.json()
        price = data.get(coin, {}).get("usd")

        if not price:
            raise ValueError("Preço não encontrado na resposta")

        # Geração simples de VWAP estimado (últimos 5% abaixo do preço atual)
        vwap = round(price * 0.95, 2)

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "vwap": vwap,
            "source": "CoinGecko"
        }

    except Exception as e:
        logger.error(f"❌ Erro ao buscar {symbol} no CoinGecko: {e}")
        return {"symbol": symbol, "error": str(e)}

# ---------------------------------------------------------
# 🔹 Twelve Data: forex e ouro
# ---------------------------------------------------------
def fetch_twelvedata(symbol):
    if not TWELVE_API_KEY:
        return {"symbol": symbol, "error": "TWELVE_API_KEY ausente"}

    # Mapear os símbolos corretos
    symbol_map = {
        "EURUSD": "EUR/USD",
        "XAUUSD": "XAU/USD"
    }

    api_symbol = symbol_map.get(symbol, symbol)
    url = f"https://api.twelvedata.com/price?symbol={api_symbol}&apikey={TWELVE_API_KEY}"

    try:
        logger.info(f"🔹 Buscando {symbol} ({api_symbol}) no Twelve Data...")
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if "price" not in data:
            raise ValueError(data.get("message", "Sem campo 'price' na resposta"))

        price = float(data["price"])
        vwap = round(price * 0.999, 4)  # leve ajuste para exibição

        return {
            "symbol": symbol,
            "price": round(price, 4),
            "vwap": vwap,
            "source": "Twelve Data"
        }

    except Exception as e:
        logger.error(f"❌ Erro ao buscar {symbol} na Twelve Data: {e}")
        return {"symbol": symbol, "error": str(e)}

# ---------------------------------------------------------
# 🔹 Consolida todos os ativos
# ---------------------------------------------------------
def get_all_assets_data():
    assets = ["BTCUSDT", "ETHUSDT", "EURUSD", "XAUUSD"]
    results = {}

    for asset in assets:
        if asset in ["BTCUSDT", "ETHUSDT"]:
            results[asset] = fetch_coingecko(asset)
        else:
            results[asset] = fetch_twelvedata(asset)

    return results
