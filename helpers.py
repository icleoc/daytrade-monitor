import requests
import pandas as pd
import numpy as np

# Endpoint público da Binance para dados spot
BINANCE_API = "https://api.binance.com/api/v3/klines"

def get_symbol_data(symbol):
    pair = symbol.upper().replace("USD", "USDT")
    url = f"{BINANCE_API}?symbol={pair}&interval=1m&limit=100"
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        raise ValueError(f"Erro ao buscar dados: {r.text}")

    df = pd.DataFrame(r.json(), columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "trades", "taker_base", "taker_quote", "ignore"
    ])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    df["vwap"] = (df["volume"] * (df["high"] + df["low"] + df["close"]) / 3).cumsum() / df["volume"].cumsum()

    # Identifica sinais
    df["signal"] = np.where(df["close"] > df["vwap"], "buy",
                    np.where(df["close"] < df["vwap"], "sell", "hold"))

    latest = df.iloc[-1]

    return {
        "symbol": symbol,
        "price": round(latest["close"], 2),
        "vwap": round(latest["vwap"], 2),
        "signal": latest["signal"]
    }
