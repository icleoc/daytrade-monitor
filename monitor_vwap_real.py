# monitor_vwap_real.py
import time
import logging
import pandas as pd
import requests
from datetime import datetime, timezone
from supabase import create_client, Client
from threading import Thread

# Configurações
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"
TWELVEDATA_API_KEY = "YOUR_TWELVEDATA_API_KEY"
REFRESH_INTERVAL = 30  # segundos

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ASSETS = ["BTC-USD", "ETH-USD", "EUR/USD", "XAU/USD"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Funções utilitárias
def upsert_ativo(nome, preco, vwap, sinal):
    payload = {
        "nome": nome,
        "preco": preco,
        "vwap": vwap,
        "sinal": sinal,
        "atualizado_em": datetime.now(timezone.utc).isoformat()
    }
    try:
        supabase.table("ativos").upsert(payload, on_conflict="nome").execute()
    except Exception as e:
        logging.error(f"Erro ao upsertar no Supabase para {nome}: {e}")

def fetch_coinbase_candles(symbol):
    granularity = 60  # 1 minuto
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={granularity}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data, columns=["time","low","high","open","close","volume"])
        df = df.sort_values("time")
        return df
    except Exception as e:
        logging.warning(f"Falha ao buscar candles Coinbase {symbol}: {e}")
        return None

def fetch_twelvedata_candles(symbol):
    interval = "1min"  # Ajustado para válido
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={TWELVEDATA_API_KEY}&outputsize=30"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "values" not in data:
            raise ValueError(f"TwelveData retornou sem 'values' para {symbol}: {data}")
        df = pd.DataFrame(data["values"])
        df = df.astype({"close": float, "volume": float})
        df = df.sort_values("datetime")
        return df
    except Exception as e:
        logging.warning(f"Falha ao buscar candles TwelveData {symbol}: {e}")
        return None

def calcular_vwap(df):
    if df is None or df.empty:
        return None
    df["typical"] = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (df["typical"] * df["volume"]).sum() / df["volume"].sum()
    return vwap

def determinar_sinal(preco, vwap):
    if preco is None or vwap is None:
        return "NEUTRO"
    if preco > vwap:
        return "SELL"
    elif preco < vwap:
        return "BUY"
    else:
        return "NEUTRO"

def process_asset(symbol):
    if symbol in ["BTC-USD", "ETH-USD"]:
        df = fetch_coinbase_candles(symbol)
        preco = df["close"].iloc[-1] if df is not None else None
    else:
        df = fetch_twelvedata_candles(symbol)
        preco = df["close"].iloc[-1] if df is not None else None
    vwap = calcular_vwap(df)
    sinal = determinar_sinal(preco, vwap)
    upsert_ativo(symbol, preco, vwap, sinal)
    logging.info(f"{symbol} -> sinal={sinal} preco={preco} vwap={vwap}")

def start_bot():
    logging.info(f"Iniciando VWAP Monitor (Coinbase + TwelveData). Assets: {ASSETS}")
    while True:
        for symbol in ASSETS:
            process_asset(symbol)
        time.sleep(REFRESH_INTERVAL)

# Se for usado pelo Flask
def start_background_thread():
    thread = Thread(target=start_bot, daemon=True)
    thread.start()
