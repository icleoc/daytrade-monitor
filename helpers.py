import os
import requests
import pandas as pd

PROVIDER = "twelvedata"
API_KEY = os.getenv("TWELVE_API_KEY")

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

    required_cols = ["open", "high", "low", "close", "volume"]
    for col in required_cols:
        if col not in df.columns:
            if col == "volume":
                df[col] = 1.0
            else:
                df[col] = None

    for col in required_cols:
        try:
            df[col] = df[col].astype(float)
        except:
            pass

    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")

    return df


def compute_vwap(df):
    df["typical"] = (df["high"] + df["low"] + df["close"]) / 3
    df["cum_vol"] = df["volume"].cumsum()
    df["cum_tpv"] = (df["typical"] * df["volume"]).cumsum()

    df["vwap"] = df["cum_tpv"] / df["cum_vol"]

    df["upper"] = df["vwap"] + df["typical"].rolling(20).std()
    df["lower"] = df["vwap"] - df["typical"].rolling(20).std()

    return df


def get_symbol_data(symbol):
    return fetch_twelvedata(symbol)


def get_all_symbols_data():
    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "XAUUSD"]

    assets = []

    for sym in symbols:
        try:
            df = get_symbol_data(sym)
            df = compute_vwap(df)

            last = df.iloc[-1]

            # Formato esperado pelo dashboard
            assets.append({
                "symbol": sym,
                "last_price": float(last["close"]),
                "signal": "—",   # pode ser substituído por BUY/SELL inteligente
                "timestamps": df["datetime"].astype(str).tolist(),
                "prices": df["close"].tolist(),
                "vwap": df["vwap"].tolist()
            })

        except Exception as e:
            assets.append({
                "symbol": sym,
                "error": str(e)
            })

    return {"assets": assets}
