import logging
from binance.client import Client
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔑 Credenciais Binance (setadas no Render)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

# 🔹 Lista de ativos
ASSETS = {
    "BTCUSD": "BTCUSDT",
    "ETHUSD": "ETHUSDT",
    "EURUSD": "EURUSDT",
    "XAUUSD": "XAUUSDT"
}

def get_asset_data(symbol, interval='1h', limit=100):
    """Obtém candles da Binance"""
    try:
        logger.info(f"🔹 Coletando {symbol} ({interval}) na Binance...")
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
        logger.info(f"✅ {symbol} carregado com {len(data)} candles.")
        return data
    except Exception as e:
        logger.error(f"❌ Erro ao buscar {symbol}: {e}")
        return []

def get_all_assets_data():
    """Agrega dados de todos os ativos"""
    result = {}
    for name, pair in ASSETS.items():
        result[name] = get_asset_data(pair)
    return result
