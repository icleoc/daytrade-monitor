import os
import logging
import requests
import pandas as pd

logging.basicConfig(level=logging.INFO)
BINANCE_MIRRORS = [
    "https://api.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com"
]

TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")
TWELVE_BASE_URL = "https://api.twelvedata.com"

ASSETS = [
    {"symbol": "BTCUSDT", "source": "binance"},
    {"symbol": "ETHUSDT", "source": "binance"},
    {"symbol": "EURUSD", "source": "twelve"},
    {"symbol": "XAUUSD", "source": "twelve"},
]

def fetch_binance_data(symbol):
    for base_url in BINANCE_MIRRORS:
        try:
            logging.info(f"🔹 Buscando {symbol} (1h) na Binance ({base_url})...")
            url = f"{base_url}/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            df = pd.DataFrame(resp.json(), columns=[
                'time', 'open', 'high', 'low', 'close',
                'volume', 'close_time', 'quote_asset_volume',
                'num_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            df['close'] = df['close'].astype(float)
            df['vwap'] = (
                (df['high'].astype(float) + df['low'].astype(float) + df['close']) / 3
            ).rolling(20).mean()
            price = float(df['close'].iloc[-1])
            vwap = float(df['vwap'].iloc[-1])
            logging.info(f"✅ {symbol}: dados prontos.")
            return {"symbol": symbol, "price": price, "vwap": vwap}
        except Exception as e:
            logging.warning(f"⚠️ Erro com {base_url}: {e}")
    raise Exception(f"Erro ao buscar {symbol} na Binance")

def fetch_twelve_data(symbol):
    if not TWELVE_API_KEY:
        logging.error("❌ Faltando TWELVE_API_KEY nas variáveis de ambiente!")
        return {"symbol": symbol, "error": "TWELVE_API_KEY ausente"}
    try:
        logging.info(f"🔹 Buscando {symbol} (1h) na Twelve Data...")
        url = f"{TWELVE_BASE_URL}/time_series?symbol={symbol}&interval=1h&outputsize=100&apikey={TWELVE_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json().get('values', [])
        if not data:
            raise Exception("Sem dados válidos retornados")
        df = pd.DataFrame(data)
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['vwap'] = (
            (df['high'] + df['low'] + df['close']) / 3
        ).rolling(20).mean()
        price = float(df['close'].iloc[-1])
        vwap = float(df['vwap'].iloc[-1])
        return {"symbol": symbol, "price": price, "vwap": vwap}
    except Exception as e:
        logging.error(f"❌ Erro ao buscar {symbol} na Twelve Data: {e}")
        return {"symbol": symbol, "error": str(e)}

def get_all_assets_data():
    results = {}
    for asset in ASSETS:
        symbol = asset['symbol']
        try:
            if asset['source'] == "binance":
                results[symbol] = fetch_binance_data(symbol)
            else:
                results[symbol] = fetch_twelve_data(symbol)
        except Exception as e:
            logging.error(f"Erro ao buscar {symbol}: {e}")
            results[symbol] = {"symbol": symbol, "error": str(e)}
    return results
