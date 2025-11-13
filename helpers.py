import requests
import os
import pandas as pd
from datetime import datetime, timedelta

# ================================
# CONFIGURAÇÕES
# ================================

TWELVE_API_KEY = os.getenv("TWELVE_API_KEY", "34b1f0bac586484c97725bbbbddad099")
API_BASE = "https://api.twelvedata.com/time_series"

# ================================
# FUNÇÕES AUXILIARES
# ================================

def convert_timestamp(ts):
    """Converte timestamps para milissegundos."""
    return int(int(ts) / 1000) if ts > 1e12 else int(ts * 1000)


def fetch_symbol(symbol, interval="1h", outputsize=100):
    """Busca dados históricos do ativo."""
    try:
        if "USD" in symbol and not symbol.endswith("USDT"):
            # Fonte: Twelve Data (forex, metais, índices)
            if not TWELVE_API_KEY:
                return {"error": "TWELVE_API_KEY ausente", "symbol": symbol}

            params = {
                "symbol": symbol,
                "interval": interval,
                "apikey": TWELVE_API_KEY,
                "outputsize": outputsize,
            }
            r = requests.get(API_BASE, params=params)
            data = r.json()

            if "values" not in data:
                return {"error": data.get("message", "Erro desconhecido"), "symbol": symbol}

            df = pd.DataFrame(data["values"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            df = df.rename(columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume"
            })
            return df

        else:
            # Fonte: Yahoo Finance (criptos)
            import yfinance as yf
            df = yf.download(symbol.replace("USDT", "-USD"), period="7d", interval=interval)
            if df.empty:
                return {"error": f"Nenhum dado retornado para {symbol}"}
            df.reset_index(inplace=True)
            df = df.rename(columns={
                "Open": "Open",
                "High": "High",
                "Low": "Low",
                "Close": "Close",
                "Volume": "Volume"
            })
            return df

    except Exception as e:
        return {"error": f"Erro ao buscar {symbol}: {str(e)}", "symbol": symbol}


def fetch_all_symbols():
    """Busca todos os símbolos configurados."""
    symbols = ["BTCUSDT", "ETHUSDT", "EURUSD", "XAUUSD"]
    results = {}

    for symbol in symbols:
        results[symbol] = fetch_symbol(symbol)

    return results
