from flask import Flask, render_template, jsonify
from helpers import fetch_all_symbols
import pandas as pd

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/data")
def api_data():
    data = fetch_all_symbols()

    # Converter DataFrames em dicionários
    serialized = {}
    for symbol, df in data.items():
        if isinstance(df, pd.DataFrame):
            serialized[symbol] = df.tail(100).to_dict(orient="records")  # últimos 100 candles
        else:
            serialized[symbol] = df  # mensagens de erro ou dicionários

    return jsonify(serialized)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
