import yfinance as yf
import pandas as pd
import numpy as np

def get_symbol_data(symbol):
    mapping = {
        "BTCUSD": "BTC-USD",
        "ETHUSD": "ETH-USD",
        "EURUSD": "EURUSD=X",
        "XAUUSD": "XAUUSD=X"
    }

    ticker = mapping.get(symbol, symbol)
    data = yf.download(ticker, period="1d", interval="15m")
    if data.empty:
        raise ValueError(f"Sem dados para {symbol}")

    data["vwap"] = (data["Volume"] * (data["High"] + data["Low"] + data["Close"]) / 3).cumsum() / data["Volume"].cumsum()
    data["signal"] = np.where(data["Close"] > data["vwap"], "buy",
                       np.where(data["Close"] < data["vwap"], "sell", "hold"))

    latest = data.iloc[-1]
    return {
        "symbol": symbol,
        "price": round(latest["Close"], 2),
        "vwap": round(latest["vwap"], 2),
        "signal": latest["signal"],
        "chart": data.tail(100).reset_index().to_dict(orient="records")
    }
