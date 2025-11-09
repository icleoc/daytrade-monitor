import os
import time
import threading
from datetime import datetime, timezone

import pandas as pd
from flask import Flask, render_template_string
from supabase import create_client, Client
from binance.client import Client as BinanceClient

# =========================================
# CONFIGURAÇÕES GERAIS
# =========================================
REFRESH_SECONDS = 30  # Tempo em segundos para o refresh automático no dashboard

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
binance_client = BinanceClient(BINANCE_API_KEY, BINANCE_API_SECRET)

ASSETS = ["BTCUSDT", "ETHUSDT", "XAUUSDT", "EURUSDT"]

app = Flask(__name__)


# =========================================
# FUNÇÃO VWAP
# =========================================
def calculate_vwap(df):
    if df.empty:
        return None
    df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
    df["tp_vol"] = df["typical_price"] * df["volume"]
    return df["tp_vol"].sum() / df["volume"].sum()


# =========================================
# ATUALIZAÇÃO DOS DADOS NO SUPABASE
# =========================================
def fetch_and_update():
    while True:
        for symbol in ASSETS:
            try:
                klines = binance_client.get_klines(symbol=symbol, interval="2m", limit=50)
                df = pd.DataFrame(
                    klines,
                    columns=[
                        "time_open", "open", "high", "low", "close", "volume",
                        "time_close", "qav", "num_trades", "taker_base_vol",
                        "taker_quote_vol", "ignore"
                    ],
                )
                df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)

                vwap = calculate_vwap(df)
                last_close = df["close"].iloc[-1]

                if last_close > vwap:
                    signal = "BUY"
                elif last_close < vwap:
                    signal = "SELL"
                else:
                    signal = "NEUTRO"

                supabase.table("ativos").upsert({
                    "nome": symbol,
                    "preco": round(last_close, 4),
                    "vwap": round(vwap, 4),
                    "sinal": signal,
                    "atualizado_em": datetime.now(timezone.utc).isoformat()
                }).execute()

                print(f"[{datetime.now()}] {symbol} atualizado -> {signal} (Preço: {last_close}, VWAP: {vwap})")

            except Exception as e:
                print(f"⚠️ Erro ao atualizar {symbol}: {e}")

        time.sleep(REFRESH_SECONDS)


# =========================================
# DASHBOARD HTML
# =========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VWAP Monitor</title>
    <style>
        body {
            background-color: #0d1117;
            color: #fff;
            font-family: Arial, sans-serif;
            text-align: center;
        }
        h1 { margin-top: 20px; }
        .cards {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 40px;
        }
        .card {
            width: 240px;
            margin: 12px;
            padding: 20px;
            border-radius: 16px;
            font-weight: bold;
            box-shadow: 0 0 12px rgba(255,255,255,0.1);
            transition: transform 0.2s ease;
        }
        .card:hover { transform: scale(1.03); }
        .buy { background-color: #1ea14b; }
        .sell { background-color: #d93d3d; }
        .neutral { background-color: #444; }
        .footer {
            margin-top: 40px;
            font-size: 14px;
            color: #aaa;
        }
    </style>
    <script>
        setTimeout(() => {
            location.reload();
        }, {{ refresh_time }} * 1000);
    </script>
</head>
<body>
    <h1>📊 VWAP Monitor — Atualização a cada {{ refresh_time }}s</h1>
    <div class="cards">
        {% if ativos and ativos|length > 0 %}
            {% for ativo in ativos %}
            <div class="card {% if ativo.sinal == 'BUY' %}buy{% elif ativo.sinal == 'SELL' %}sell{% else %}neutral{% endif %}">
                <h2>{{ ativo.nome }}</h2>
                <p>💰 Preço: {{ ativo.preco }}</p>
                <p>📈 VWAP: {{ ativo.vwap }}</p>
                <p>📊 Sinal: {{ ativo.sinal }}</p>
                <p><small>⏱ Atualizado: {{ ativo.atualizado_em[:19].replace('T',' ') }}</small></p>
            </div>
            {% endfor %}
        {% else %}
            <h3>Nenhum dado disponível ainda...</h3>
        {% endif %}
    </div>
    <div class="footer">Powered by Flask + Binance + Supabase</div>
</body>
</html>
"""


# =========================================
# ROTA PRINCIPAL
# =========================================
@app.route("/")
def index():
    try:
        response = supabase.table("ativos").select("*").execute()
        data = response.data or []
        data = sorted(data, key=lambda x: x["nome"])
    except Exception as e:
        print(f"Erro ao carregar dashboard: {e}")
        data = []
    return render_template_string(HTML_TEMPLATE, ativos=data, refresh_time=REFRESH_SECONDS)


# =========================================
# THREAD PRINCIPAL
# =========================================
if __name__ == "__main__":
    print("🚀 Iniciando VWAP Monitor em tempo real...")
    thread = threading.Thread(target=fetch_and_update, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
