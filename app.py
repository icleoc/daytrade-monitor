# app.py
import os
import time
import math
from datetime import datetime
from flask import Flask, jsonify, render_template, send_from_directory
import requests
import pandas as pd

app = Flask(__name__, static_folder='static', template_folder='templates')

# Config
SYMBOLS = [
    {"name": "BTCUSD", "fsym": "BTC", "tsym": "USD", "exchange": "Binance"},
    {"name": "ETHUSD", "fsym": "ETH", "tsym": "USD", "exchange": "Binance"},
    {"name": "EURUSD", "fsym": "EUR", "tsym": "USD", "exchange": ""},   # FX via CryptoCompare (if available)
    {"name": "XAUUSD", "fsym": "XAU", "tsym": "USD", "exchange": ""},   # Gold (XAU) as symbol
]

# CryptoCompare settings
CRYPTOCOMPARE_BASE = "https://min-api.cryptocompare.com/data/v2/histominute"
API_KEY = os.environ.get("CRYPTOCOMPARE_API_KEY")  # optional but recommended
AGGREGATE_MINUTES = 15
LIMIT = 500  # number of aggregated 15m bars - adjust as needed (limit+1 bars returned)

# VWAP/Bands settings
ROLL_WINDOW = 20   # rolling std window (in 15m bars) used for bands (adjustable)
BANDS_K = 2.0      # multiplier for std to form upper/lower bands

HEADERS = {}
if API_KEY:
    HEADERS['authorization'] = f'Apikey {API_KEY}'

def fetch_histominute(fsym, tsym="USD", aggregate=15, limit=500, exchange=""):
    """
    Fetch aggregated minute history from CryptoCompare.
    Uses histominute with aggregate to get X-minute bars.
    """
    params = {
        "fsym": fsym,
        "tsym": tsym,
        "limit": limit,
        "aggregate": aggregate,
    }
    if exchange:
        params["e"] = exchange
    url = CRYPTOCOMPARE_BASE
    r = requests.get(url, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("Response") == "Error":
        raise RuntimeError(f"CryptoCompare error: {data.get('Message')}")
    bars = data.get("Data", {}).get("Data", [])
    return pd.DataFrame(bars)

def compute_vwap_and_bands(df):
    """
    df expected to have columns: time, open, high, low, close, volumefrom, volumeto
    returns df with vwap, upper, lower and a 'signal' if VWAP-cross happened on last candle.
    """
    if df.empty:
        return df

    # convert time to datetime
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['time'], unit='s')
    df = df.sort_values('timestamp').reset_index(drop=True)

    # typical price
    df['typ'] = (df['high'] + df['low'] + df['close']) / 3.0

    # choose volume - use volumeto (quote currency) if available, else volumefrom
    vol_col = 'volumeto' if 'volumeto' in df.columns else 'volumefrom'
    df['vol_quote'] = df[vol_col].fillna(0.0)

    # cumulative VWAP: sum(typ * vol) / sum(vol)
    # handle zero volumes
    df['tpv'] = df['typ'] * df['vol_quote']
    df['cum_tpv'] = df['tpv'].cumsum()
    df['cum_vol'] = df['vol_quote'].cumsum().replace(0, float('nan'))
    df['vwap'] = df['cum_tpv'] / df['cum_vol']
    # if cum_vol zero initially, vwap may be NaN - fill forward/back
    df['vwap'] = df['vwap'].ffill().bfill()

    # Rolling std of typical price
    df['tp_std'] = df['typ'].rolling(window=ROLL_WINDOW, min_periods=1).std().fillna(0.0)

    df['upper'] = df['vwap'] + (BANDS_K * df['tp_std'])
    df['lower'] = df['vwap'] - (BANDS_K * df['tp_std'])

    # signal logic: buy when close crosses above vwap; sell when close crosses below vwap
    df['prev_close'] = df['close'].shift(1)
    df['prev_vwap'] = df['vwap'].shift(1)

    df['signal'] = None
    mask_buy = (df['prev_close'] <= df['prev_vwap']) & (df['close'] > df['vwap'])
    mask_sell = (df['prev_close'] >= df['prev_vwap']) & (df['close'] < df['vwap'])
    df.loc[mask_buy, 'signal'] = 'buy'
    df.loc[mask_sell, 'signal'] = 'sell'

    # only keep needed columns for JSON
    return df

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/data")
def api_data():
    """
    Returns JSON of candle arrays and computed indicators for each symbol.
    """
    out = {}
    for s in SYMBOLS:
        name = s['name']
        try:
            df = fetch_histominute(s['fsym'], s['tsym'], aggregate=AGGREGATE_MINUTES, limit=LIMIT, exchange=s.get('exchange', ''))
            if df.empty:
                out[name] = {"error": "no-data"}
                continue
            df = compute_vwap_and_bands(df)

            # prepare arrays
            candles = []
            for _, row in df.iterrows():
                candles.append({
                    "time": int(row['time']),  # epoch
                    "timestamp": row['timestamp'].isoformat(),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volumefrom": float(row.get('volumefrom', 0.0) or 0.0),
                    "volumeto": float(row.get('volumeto', 0.0) or 0.0),
                    "vwap": None if pd.isna(row['vwap']) else float(row['vwap']),
                    "upper": None if pd.isna(row['upper']) else float(row['upper']),
                    "lower": None if pd.isna(row['lower']) else float(row['lower']),
                    "signal": row['signal'] if row['signal'] else None
                })

            # last signal (if any)
            last_signals = df.loc[df['signal'].notna(), ['timestamp', 'signal']]
            last_signal = None
            if not last_signals.empty:
                last = last_signals.iloc[-1]
                last_signal = {"timestamp": last['timestamp'].isoformat(), "signal": last['signal']}

            out[name] = {
                "symbol": name,
                "fsym": s['fsym'],
                "tsym": s['tsym'],
                "timeframe_minutes": AGGREGATE_MINUTES,
                "candles": candles,
                "last_signal": last_signal
            }
        except Exception as e:
            out[name] = {"error": str(e)}

    return jsonify({"generated_at": datetime.utcnow().isoformat() + "Z", "data": out})

if __name__ == "__main__":
    # For production use gunicorn / uvicorn wsgi. For dev:
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
