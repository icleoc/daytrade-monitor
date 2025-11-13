# helpers.py
import os
import time
import logging
import requests
import pandas as pd
from datetime import datetime
from functools import lru_cache

TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")
BASE_TWELVE_URL = "https://api.twelvedata.com/time_series"
BASE_COINGECKO_URL = "https://api.coingecko.com/api/v3"

# Última hora da requisição para limitar chamadas a 1 por minuto
_last_request_time = {}

logging.basicConfig(level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")

def rate_limited(symbol):
    """Limita chamadas a 1 por minuto por ativo."""
    now = time.time()
    last_time = _last_request_time.get(symbol, 0)
    if now - last_time < 60:
        return False
    _last_request_time[symbol] = now
    return True

def fetch_twelve_data(symbol, interval="15m"):
    """Busca dados OHLC da Twelve Data."""
    if not rate_limited(symbol):
        return None  # Não faz requisição se não passou 60s
    
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": TWELVE_API_KEY,
        "outputsize": 500  # mais pontos para cálculo VWAP
    }
    try:
        response = requests.get(BASE_TWELVE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "values" in data:
            df = pd.DataFrame(data["values"])
            df = df.iloc[::-1]  # ordena do mais antigo para o mais recente
            df["datetime"] = pd.to_datetime(df["datetime"])
            df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
            return df
        else:
            logging.error(f"Erro Twelve Data para {symbol}: {data}")
            return None
    except Exception as e:
        logging.error(f"Erro Twelve Data para {symbol}: {e}")
        return None

def fetch_coin(symbol, fallback_coin):
    """Busca dados do CoinGecko como fallback."""
    if not rate_limited(symbol):
        return None
    try:
        url = f"{BASE_COINGECKO_URL}/coins/{fallback_coin}/market_chart"
        params = {"vs_currency": "usd", "days": 7, "interval": "minute"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("datetime", inplace=True)
        df["close"] = df["price"]
        return df
    except Exception as e:
        logging.error(f"Erro ao buscar {symbol} no CoinGecko: {e}")
        return None

def calculate_vwap(df):
    """Calcula VWAP e bandas superiores/inferiores."""
    df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
    df["upper_band"] = df["vwap"] + df["close"].rolling(20).std()
    df["lower_band"] = df["vwap"] - df["close"].rolling(20).std()
    return df

def generate_signals(df):
    """Sinaliza compra e venda baseado em cruzamento com bandas VWAP."""
    signals = []
    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["upper_band"].iloc[i] and df["close"].iloc[i-1] <= df["upper_band"].iloc[i-1]:
            signals.append({"datetime": df["datetime"].iloc[i], "signal": "SELL", "price": df["close"].iloc[i]})
        elif df["close"].iloc[i] < df["lower_band"].iloc[i] and df["close"].iloc[i-1] >= df["lower_band"].iloc[i-1]:
            signals.append({"datetime": df["datetime"].iloc[i], "signal": "BUY", "price": df["close"].iloc[i]})
    return signals

def get_all_data():
    """Agrega dados de todos os ativos e sinais."""
    symbols_info = {
        "BTCUSDT": {"interval": "15m", "fallback": "bitcoin"},
        "ETHUSDT": {"interval": "15m", "fallback": "ethereum"},
        "EURUSD": {"interval": "15m", "fallback": None},
        "XAUUSD": {"interval": "15m", "fallback": None},
    }

    results = {}
    for symbol, info in symbols_info.items():
        df = fetch_twelve_data(symbol, interval=info["interval"])
        if df is None and info["fallback"]:
            df = fetch_coin(symbol, info["fallback"])
        if df is None:
            results[symbol] = {"last": None, "signals": [], "error": "Sem dados"}
            continue
        
        df = calculate_vwap(df)
        signals = generate_signals(df)
        last_price = df["close"].iloc[-1] if not df.empty else None
        results[symbol] = {"last": last_price, "signals": signals, "error": None}
    
    return results
