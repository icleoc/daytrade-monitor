from flask import Flask, render_template, jsonify
from helpers import fetch_all_symbols
import pandas as pd

app = Flask(__name__)

# Lista de símbolos padrão que o dashboard usa
SYMBOLS = ["BTCUSDT", "ETHUSDT", "EURUSD", "XAUUSD"]

@app.route("/")
def dashboard():
    # Passamos a lista de símbolos para o template
    return render_template("dashboard.html", symbols=SYMBOLS)

@app.route("/api/data")
def api_data():
    data = fetch_all_symbols()

    # Converter DataFrames em dicionários
    serialized = {}
    for symbol, df in data.items():
        if isinstance(df, pd.DataFrame):
            serialized[symbol] = df.tail(100).to_dict(orient="records")
        else:
            serialized[symbol] = df  # mensagens de erro, etc.

    return jsonify(serialized)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
