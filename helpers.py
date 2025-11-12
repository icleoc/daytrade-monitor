import logging
from binance.client import Client
import os
from datetime import datetime
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- API KEYS (já configuradas no Render) ----
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

# ---- Lista de ativos ----
ASSETS = {
    "BTCUSD": "BTCUSDT",
    "ETHUSD": "ETHUSDT",
    "EURUSD": "EURUSDT",
    "XAUUSD": "XAUUSDT"
}

def get_asset_data(symbol: str, interval='1h', limit=100):
    """Obtém candles de um ativo na Binance"""
    try:
        logger.info(f"🔹 Buscando {symbol} ({interval}) na Binance...")
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        data = []
        for k in klines:
            data.append({
                "timestamp": datetime.fromtimestamp(k[0]/1000).strftime('%Y-%m-%d %H:%M'),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5])
            })
        logger.info(f"✅ Binance retornou {len(data)} candles para {symbol}")
        return data
    except Exception as e:
        logger.error(f"❌ Erro ao buscar {symbol}: {e}")
        return []

def get_all_assets_data():
    """Coleta dados de todos os ativos"""
    all_data = {}
    for name, pair in ASSETS.items():
        all_data[name] = get_asset_data(pair)
    return all_data
