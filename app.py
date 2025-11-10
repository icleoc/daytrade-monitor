# app.py
from flask import Flask, render_template, jsonify
from helpers import (
    fetch_crypto_compare_histo,
    compute_vwap_and_bands,
    compute_signal,
)
from config import SYMBOLS, UPDATE_INTERVAL_SECONDS
import traceback

app = Flask(__name__)

@app.route("/")
def index():
    """Página principal (dashboard)."""
    return render_template(
        "dashboard.html",
        symbols=[s["symbol"] for s in SYMBOLS],
        update_interval=UPDATE_INTERVAL_SECONDS,
    )

@app.route("/api/data")
def api_data():
    """Endpoint que fornece dados atualizados de preço e sinal."""
    data = []
    for s in SYMBOLS:
        sym = s["symbol"]
        try:
            df = fetch_crypto_compare_histo(sym)
            vwap_data = compute_vwap_and_bands(df)
            last_signal = compute_signal(vwap_data)
            data.append({
                "symbol": sym,
                "price": float(vwap_data["close"].iloc[-1]),
                "signal": last_signal,
                "chart": vwap_data.tail(50).to_dict(orient="records"),
            })
        except Exception as e:
            print(f"[ERRO] Falha ao processar {sym}: {e}")
            traceback.print_exc()
            data.append({
                "symbol": sym,
                "error": str(e),
                "chart": [],
                "signal": "ERROR",
                "price": None,
            })
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
