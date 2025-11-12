import requests
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fonte pública da Binance (sem API key)
BINANCE_BASE_URL = "https://api.binance.com/api/v3/klines"

# Twelve Data para Forex e Ouro (EURUSD e XAUUSD)
TWELVE_API_KEY = "SUA_CHAVE_TWELVE_API"
TWELVE_BASE_URL = "https://api.twelvedata.com/time_series"

def fetch_binance_symbol(symbol: str, interval: str = "1h", limit: int = 100):
    """Busca candles da Binance sem autenticação (criptos)."""
    logger.info(f"🔹 Buscando {symbol} ({interval}) na Binance pública...")
    try:
        response = requests.get(
            BINANCE_BASE_URL,
            params={"symbol": symbol, "interval": interval, "limit": limit}
        )
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close",
            "volume", "close_time", "qav", "num_trades",
            "taker_base_vol", "taker_quote_vol", "ignore"
        ])
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df["close"] = df["close"].astype(float)
        return df[["open_time", "close"]]
    except Exception as e:
        logger.error(f"❌ Erro ao buscar {symbol} na Binance: {e}")
        return pd.DataFrame()

def fetch_twelvedata_symbol(symbol: str, interval: str = "1h", outputsize: int = 100):
    """Busca candles de ativos não cripto (EURUSD, XAUUSD)."""
    logger.info(f"🔹 Buscando {symbol} ({interval}) na Twelve Data...")
    try:
        response = requests.get(
            TWELVE_BASE_URL,
            params={
                "symbol": symbol,
                "interval": interval,
                "apikey": TWELVE_API_KEY,
                "outputsize": outputsize
            }
        )
        response.raise_for_status()
        data = response.json()
        values = data.get("values", [])
        df = pd.DataFrame(values)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["close"] = df["close"].astype(float)
        return df[["datetime", "close"]].rename(columns={"datetime": "open_time"})
    except Exception as e:
        logger.error(f"❌ Erro ao buscar {symbol} na Twelve Data: {e}")
        return pd.DataFrame()

def get_asset_data(symbol: str, interval: str = "1h"):
    """Seleciona automaticamente a fonte conforme o ativo."""
    if symbol in ["BTCUSDT", "ETHUSDT"]:
        return fetch_binance_symbol(symbol, interval)
    elif symbol in ["EUR/USD", "XAU/USD"]:
        return fetch_twelvedata_symbol(symbol.replace("/", ""), interval)
    else:
        logger.warning(f"⚠️ Ativo {symbol} não reconhecido.")
        return pd.DataFrame()
