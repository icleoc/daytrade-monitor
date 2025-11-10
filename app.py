# app.py
from flask import Flask, render_template, jsonify
from config import SYMBOLS, TIMEFRAME_MINUTES, CANDLE_LIMIT, BAND_STD_MULTIPLIER, UPDATE_INTERVAL_SECONDS
from helpers import fetch_crypto_compare_histo, fetch_exchange_rate_ohlc, compute_vwap_and_bands, compute_signal
import traceback

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    # main dashboard
    return render_template("dashboard.html", symbols=SYMBOLS, update_interval=UPDATE_INTERVAL_SECONDS)


@app.route("/api/data")
def api_data():
    results = {}
    errors = {}
    for s in SYMBOLS:
        sym = s["symbol"]
        base = s["exchange_symbol"]
        quote = s["quote"]
        try:
            # fetch candles (for cryptos we use CryptoCompare)
            if base in ["BTC", "ETH", "XRP", "LTC", "BCH"] or sym.endswith("USD"):
                # try crypto compare for crypto symbols
                if base in ["BTC", "ETH"]:
                    df = fetch_crypto_compare_histo(base, quote, aggregate_minutes=TIMEFRAME_MINUTES, limit=CANDLE_LIMIT)
                else:
                    # attempt to fetch via crypto compare too
                    try:
                        df = fetch_crypto_compare_histo(base, quote, aggregate_minutes=TIMEFRAME_MINUTES, limit=CANDLE_LIMIT)
                    except Exception:
                        df = fetch_exchange_rate_ohlc(base+quote, aggregate_minutes=TIMEFRAME_MINUTES, limit=CANDLE_LIMIT)
            else:
                df = fetch_exchange_rate_ohlc(base+quote, aggregate_minutes=TIMEFRAME_MINUTES, limit=CANDLE_LIMIT)

            df = compute_vwap_and_bands(df, std_multiplier=BAND_STD_MULTIPLIER)
            sig = compute_signal(df)
            # prepare json serializable
            rows = []
            for _, r in df.tail(200).iterrows():
                rows.append({
                    "datetime": r['datetime'].isoformat(),
                    "open": float(r['open']),
                    "high": float(r['high']),
                    "low": float(r['low']),
                    "close": float(r['close']),
                    "volume": float(r['volume']),
                    "vwap": float(r['vwap']),
                    "upper": float(r['upper_band']),
                    "lower": float(r['lower_band']),
                })
            results[sym] = {"data": rows, "signal": sig}
        except Exception as e:
            errors[sym] = str(e) + "\n" + traceback.format_exc(limit=1)
            results[sym] = {"data": [], "signal": {"signal": "NEUTRAL", "reason": "error fetching", "time": None}}
    return jsonify({"results": results, "errors": errors})

if __name__ == "__main__":
    # para dev local
    app.run(host="0.0.0.0", port=5000, debug=False)
