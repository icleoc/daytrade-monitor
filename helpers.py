import os
import requests
import yfinance as yf
import pandas as pd


# -------------------------------------------------------------------
# VWAP + UPPER/LOWER BAND CALC
# -------------------------------------------------------------------
def calculate_vwap_bands(df, band_multiplier=0.2):
    df["typical"] = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (df["typical"] * df["volume"]).cumsum() / df["volume"].cumsum()

    df["upper"] = df["vwap"] * (1 + band_multiplier)
    df["lower"] = df["vwap"] * (1 - band_multiplier)
    return df


# -------------------------------------------------------------------
# SIGNAL ENGINE
# -------------------------------------------------------------------
def generate_signals(df):
    df["signal"] = "none"

    # BUY: candle fechou acima da upper
    df.loc[df["close"] > df["upper"], "signal"] = "buy"

    # SELL: candle fechou abaixo da lower
    df.loc[df["close"] < df["lower"], "signal"] = "sell"

    return df


# -------------------------------------------------------------------
# FETCH CRYPTO FROM YFINANCE (15m)
# -------------------------------------------------------------------
def fetch_crypto(symbol):
    ticker = yf.Ticker(symbol)
    df = ticker.history(interval="15m", period="2d")

    if df.empty:
        return None

    df = df.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )

    df = df[["open", "high", "low", "close", "volume"]]
    df = calculate_vwap_bands(df)
    df = generate_signals(df)

    return df


# -------------------------------------------------------------------
# FETCH FOREX / METALS FROM TWELVE DATA (15m)
# -------------------------------------------------------------------
def fetch_twelvedata(symbol):
    api_key = os.getenv("TWELVE_API_KEY")
    if not api_key:
        raise Exception("TWELVE_API_KEY não encontrado no Render")

    url = (
        f"https://api.twelvedata.com/time_series?symbol={symbol}"
        f"&interval=15min&apikey={api_key}&outputsize=200"
    )

    response = requests.get(url).json()

    if "values" not in response:
        print("Erro Twelve:", response)
        return None

    data = response["values"]

    df = pd.DataFrame(data)
    df = df.rename(
        columns={
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        }
    )

    df = df.astype(
        {"open": float, "high": float, "low": float, "close": float, "volume": float}
    )

    df = df[::-1]  # inverter ordem: mais antigo → mais novo

    df = calculate_vwap_bands(df)
    df = generate_signals(df)

    return df


# -------------------------------------------------------------------
# MASTER DISPATCH (AUTO CHOOSE PROVIDER)
# -------------------------------------------------------------------
def get_symbol_data(symbol):
    crypto_list = ["BTC-USD", "ETH-USD"]

    if symbol in crypto_list:
        return fetch_crypto(symbol)
    else:
        return fetch_twelvedata(symbol)


# -------------------------------------------------------------------
# MULTIPLE SYMBOLS
# -------------------------------------------------------------------
def get_all_symbols_data():
    mapping = {
        "BTC/USDT": "BTC-USD",
        "ETH/USDT": "ETH-USD",
        "EUR/USD": "EUR/USD",
        "XAU/USD": "XAU/USD",
    }

    results = {}

    for label, real_symbol in mapping.items():
        df = get_symbol_data(real_symbol)
        if df is not None:
            results[label] = df.tail(120).to_dict(orient="list")

    return results

