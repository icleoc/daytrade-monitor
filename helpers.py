import requests
import pandas as pd
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mirrors públicos da Binance (sem bloqueio)
BINANCE_URLS = [
    "https://api1.binance.com/api/v3/klines",
    "https://data-api.binance.vision/api/v3/klines"
]

# Twelve Data
TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")
TWELVE_BASE_URL = "https://api.twelvedata.com/time_series"

def fetch_binance_symbol(symbol: str, interval: str = "1h", limit: int = 100):
    """Busca candles da Binance por mirrors públicos."""
    logger.info(f"🔹 Buscando {symbol} ({interval}) na Binance (mirror)...")
    for base_url in BINANCE_URLS:
        try:
            response = requests.get(
                base_url,
                params={"symbol": symbol, "interval": interval, "limit": limit},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                raise ValueError("Resposta inesperada da Binance")
            df = pd.DataFrame(data, columns=[
                "open_time", "open", "high", "low", "close",
                "volume", "close_time", "qav", "num_trades",
                "taker_base_vol", "taker_quote_vol", "ignore"
            ])
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
            df["close"] = df["close"].astype(float)
            logger.info(f"✅ {symbol}: {len(df)} candles recebidos da Binance mirror.")
            return df[["open_time", "close"]]
        except Exception as e:
            logger.warning(f"⚠️ Tentativa falhou em {base_url}: {e}")
    logger.error(f"❌ Falha total ao buscar {symbol} em todos os mirrors da Binance.")
    return pd.DataFrame()

def fetch_twelvedata_symbol(symbol: str, interval: str = "1h", outputsize: int = 100):
    """Busca candles de ativos não cripto (EURUSD, XAUUSD) via Twelve Data."""
    logger.info(f"🔹 Buscando {symbol} ({interval}) na Twelve Data...")
    if not TWELVE_API_KEY:
        logger.error("❌ Faltando TWELVE_API_KEY nas variáveis de ambiente!")
        return pd.DataFrame()
    try:
        response = requests.get(
            TWELVE_BASE_URL,
            params={
                "symbol": symbol,
                "interval": interval,
                "apikey": TWELVE_API_KEY,
                "outputsize": outputsize
            },
            timeout=10
        )
        data = response.json()
        if "values" not in data:
            logger.error(f"❌ Erro Twelve Data: {data.get('message', 'resposta inválida')}")
            return pd.DataFrame()
        df = pd.DataFrame(data["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["close"] = df["close"].astype(float)
        df.rename(columns={"datetime": "open_time"}, inplace=True)
        logger.info(f"✅ {symbol}: {len(df)} candles recebidos da Twelve Data.")
        return df[["open_time", "close"]]
    except Exception as e:
        logger.error(f"❌ Erro ao buscar {symbol} na Twelve Data: {e}")
        return pd.DataFrame()

def get_asset_data(symbol: str, interval: str = "1h"):
    """Seleciona automaticamente a fonte conforme o ativo."""
    if symbol in ["BTCUSDT", "ETHUSDT"]:
        return fetch_binance_symbol(symbol, interval)
    elif symbol in ["EURUSD", "XAUUSD", "EUR/USD", "XAU/USD"]:
        return fetch_twelvedata_symbol(symbol.replace("/", ""), interval)
    else:
        logger.warning(f"⚠️ Ativo {symbol} não reconhecido.")
        return pd.DataFrame()
