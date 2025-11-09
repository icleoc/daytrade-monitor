import os
import time
import requests
import pandas as pd
from flask import Flask, render_template, jsonify
from supabase import create_client, Client
from datetime import datetime, timezone

# --- Configurações ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ativos a monitorar (Coinbase usa hífen)
ASSETS = ["BTC-USD", "ETH-USD", "XAU-USD", "EUR-USD"]
REFRESH_INTERVAL = 120  # segundos (2 min timeframe)

# Flask app
app = Flask(__name__)

# --- Funções principais ---

def get_coinbase_data(symbol):
    """Obtém candles de 2 minutos da Coinbase"""
    try:
        url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity=120"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Coinbase retorna [time, low, high, open, close, volume]
        df = pd.DataFrame(data, columns=["time", "low", "high", "open", "close", "volume"])
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df.sort_values("time", inplace=True)
        df.reset_index(drop=True, inplace=True)

        # cálculo VWAP
        df["tp"] = (df["high"] + df["low"] + df["close"]) / 3
        vwap = (df["tp"] * df["volume"]).sum() / df["volume"].sum()

        last_close = df.iloc[-1]["close"]
        sinal = "BUY" if last_close > vwap else "SELL"

        return {
            "symbol": symbol,
            "price": round(float(last_close), 2),
            "vwap": round(float(vwap), 2),
            "sinal": sinal
        }

    except Exception as e:
        print(f"Erro ao obter dados {symbol}: {e}")
        return None


def update_supabase_record(data):
    """Atualiza ou insere o ativo no Supabase"""
    try:
        supabase.table("ativos").upsert({
            "nome": data["symbol"],
            "preco": data["price"],
            "vwap": data["vwap"],
            "sinal": data["sinal"],
            "atualizado_em": datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception as e:
        print(f"Erro Supabase {data['symbol']}: {e}")


def start_all():
    """Loop principal do bot"""
    print("🚀 VWAP Monitor iniciado (Coinbase + Supabase)...")
    while True:
        for asset in ASSETS:
            info = get_coinbase_data(asset)
            if info:
                update_supabase_record(info)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {asset} => {info['sinal']} | Preço: {info['price']} | VWAP: {info['vwap']}")
        time.sleep(REFRESH_INTERVAL)


# --- Flask rotas ---

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/signals")
def api_signals():
    """Retorna dados atuais dos ativos"""
    try:
        data = supabase.table("ativos").select("*").execute().data
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
