import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# ========================
# Configuração das APIs
# ========================
BINANCE_BASE_URL = "https://api.binance.com/api/v3/klines"
TWELVE_BASE_URL = "https://api.twelvedata.com/time_series"

TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")

# ========================
# Função principal: get_symbol_data
# ========================
def get_symbol_data(symbol: str, timeframe: str = "1h"):
    """
    Retorna dados do ativo (DataFrame) com OHLC e VWAP calculado.
    A origem é Binance para criptoativos e TwelveData para forex/metais.
    """
    symbol = symbol.upper()
    if symbol in ["BTCUSD", "ETHUSD"]:
        return url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit=100"
    elif symbol in ["EURUSD", "XAUUSD"]:
        return get_from_twelve_data(symbol, timeframe)
    else:
        raise ValueError(f"Ativo {symbol} não suportado.")


# ========================
# Binance
# ========================
def url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit=100":
    pair = symbol.replace("USD", "USDT")
    params = {"symbol": pair, "interval": interval, "limit": 100}

    response = requests.get(BINANCE_BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "_ignore1", "_ignore2", "_ignore3", "_ignore4", "_ignore5", "_ignore6"
    ])

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    df["vwap"] = (df["volume"] * (df["high"] + df["low"] + df["close"]) / 3).cumsum() / df["volume"].cumsum()
    return df.tail(1).to_dict(orient="records")[0]


# ========================
# Twelve Data
# ========================
def get_from_twelve_data(symbol: str, interval: str):
    interval_map = {"1h": "1h", "15m": "15min", "5m": "5min"}
    interval_td = interval_map.get(interval, "1h")

    params = {
        "symbol": symbol,
        "interval": interval_td,
        "apikey": TWELVE_API_KEY,
        "outputsize": 100
    }

    response = requests.get(TWELVE_BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    if "values" not in data:
        raise Exception(f"Erro ao obter dados de {symbol}: {data}")

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    df["vwap"] = (df["volume"] * (df["high"] + df["low"] + df["close"]) / 3).cumsum() / df["volume"].cumsum()
    return df.tail(1).to_dict(orient="records")[0]
