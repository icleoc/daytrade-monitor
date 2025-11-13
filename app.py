from flask import Flask, render_template, jsonify
import threading
import time

app = Flask(__name__)

# --- CONFIGURAÇÕES DO DASHBOARD ---
# Aqui você define os ativos que o sistema deve monitorar
SYMBOLS = [
    {"symbol": "AAPL", "source": "yahoo"},
    {"symbol": "MSFT", "source": "yahoo"},
    {"symbol": "GOOG", "source": "yahoo"},
    {"symbol": "BTCUSDT", "source": "binance"},
    {"symbol": "ETHUSDT", "source": "binance"}
]

@app.route("/")
def dashboard():
    # Passa a lista SYMBOLS para o template
    return render_template("dashboard.html", symbols=SYMBOLS)

@app.route("/api/symbols")
def api_symbols():
    return jsonify(SYMBOLS)

def background_updater():
    while True:
        # Aqui depois você pode adicionar as rotinas que atualizam preços, VWAP etc.
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=background_updater, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
