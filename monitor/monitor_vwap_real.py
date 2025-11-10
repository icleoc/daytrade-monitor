import os
import asyncio
import json
import logging
import requests
import pandas as pd
from datetime import datetime
from binance.client import Client
from binance.websocket.spot.websocket_client import SpotWebsocketClient as WsClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variáveis de ambiente
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")

# Ativos
BINANCE_ASSETS = ["XAUUSDT", "BTCUSDT", "ETHUSDT"]
ALPHA_VANTAGE_ASSETS = ["EURUSD"]

# Dicionário para armazenar dados
prices = {symbol: [] for symbol in BINANCE_ASSETS + ALPHA_VANTAGE_ASSETS}

# -------------------------------
# Função para Alpha Vantage
# -------------------------------
def fetch_alpha_vantage(symbol, interval="15min"):
    logging.info(f"Buscando dados {symbol} da Alpha Vantage...")
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "FX_INTRADAY",
        "from_symbol": symbol[:3],
        "to_symbol": symbol[3:],
        "interval": interval,
        "apikey": ALPHA_VANTAGE_KEY,
        "outputsize": "compact"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        key = f"Time Series FX ({interval})"
        df = pd.DataFrame(data[key]).T
        df.columns = ["open", "high", "low", "close"]
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        logging.error(f"Erro Alpha Vantage {symbol}: {e}")
        return None

# -------------------------------
# Função para VWAP Binance
# -------------------------------
def vwap(df):
    df = df.copy()
    df['typical'] = (df['high'].astype(float) + df['low'].astype(float) + df['close'].astype(float)) / 3
    df['volume'] = df['close'].astype(float)  # se volume real estiver disponível, use
    return (df['typical'] * df['volume']).sum() / df['volume'].sum()

# -------------------------------
# WebSocket Binance
# -------------------------------
def handle_message(msg):
    if 'data' in msg:
        symbol = msg['data']['s']
        price = float(msg['data']['c'])
        timestamp = datetime.fromtimestamp(msg['data']['E']/1000)
        prices[symbol].append({'price': price, 'time': timestamp})
        logging.info(f"{symbol}: {price} @ {timestamp}")

async def start_binance_ws():
    ws_client = WsClient()
    ws_client.start()
    for asset in BINANCE_ASSETS:
        ws_client.kline(symbol=asset, interval="1m", callback=handle_message)
    while True:
        await asyncio.sleep(1)

# -------------------------------
# Loop principal
# -------------------------------
async def main():
    # Alpha Vantage inicial
    for asset in ALPHA_VANTAGE_ASSETS:
        df = fetch_alpha_vantage(asset)
        if df is not None:
            prices[asset] = df

    # Binance WebSocket
    await start_binance_ws()

if __name__ == "__main__":
    asyncio.run(main())
