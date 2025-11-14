import os
import requests
import pandas as pd


# ------------------------------------------------------------
# Provider selection
# ------------------------------------------------------------
PROVIDER = "twelvedata"
API_KEY = os.getenv("TWELVE_API_KEY")

# ------------------------------------------------------------
# Fetch data from TwelveData
# ------------------------------------------------------------
def fetch_twelvedata(symbol):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": "15min",
        "apikey": API_KEY,
        "outputsize": 200
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    if "values" not in data:
        raise Exception(f"Erro na TwelveData: {data}")

    df = pd.DataFrame(data["values"])
    df = df.rename(columns=str.lower)

    # Garantir que colunas existam
    required_cols = ["open", "high", "low", "close", "volume"]
    for col in required_cols:
        if col not in df.columns:
            # Volume pode não existir em Forex e outros: fallback = 1
            if col == "volume":
                df[col] = 1.0
            else:
                df[col] = None

    # Conversões seguras
    for col in required_cols:
        try:
            df[col] = df[col].astype(float)
        except:
            pass

    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")

    return df


# ------------------------------------------------------------
# Calculate VWAP + Bands
# ------------------------------------------------------------
def compute_vwap(df):
    df["typical"] = (df["high"] + df["low"] + df["close"]) / 3
    df["cum_vol"] = df["volume"].cumsum()
    df["cum_tpv"] = (df["typical"] * df["volume"]).cumsum()

    df["vwap"] = df["cum_tpv"] / df["cum_vol"]

    # Desvio padrão para bands
    df["upper"] = df["vwap"] + df["typical"].rolling(20).std()
    df["lower"] = df["vwap"] - df["typical"].rolling(20).std()

    return df


# ------------------------------------------------------------
# Unified fetch
# ------------------------------------------------------------
def get_symbol_data(symbol):
    return fetch_twelvedata(symbol)


# ------------------------------------------------------------
# Multiple assets processing
# ------------------------------------------------------------
def get_all_symbols_data():
    symbols = [
        "BTC/USDT",
        "ETH/USDT",
        "EUR/USD",
        "XAU/USD"
    ]

    result = {}

    for sym in symbols:
        try:
            df = get_symbol_data(sym)
            df = compute_vwap(df)

            last = df.iloc[-1]

            result[sym] = {
                "last_price": float(last["close"]),
                "vwap": float(last["vwap"]),
                "upper": float(last["upper"]) if not pd.isna(last["upper"]) else None,
                "lower": float(last["lower"]) if not pd.isna(last["lower"]) else None,
                "history": {
                    "datetime": df["datetime"].astype(str).tolist(),
                    "close": df["close"].tolist(),
                    "vwap": df["vwap"].tolist(),
                    "upper": df["upper"].tolist(),
                    "lower": df["lower"].tolist(),
                }
            }

        except Exception as e:
            result[sym] = {"error": str(e)}

    return result
