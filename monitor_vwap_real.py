import time
import requests
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
from threading import Thread
import logging

# Configurações de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Variáveis de ambiente
import os
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "30"))

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ativos
COINBASE_ASSETS = ["BTC-USD", "ETH-USD"]
TWELVEDATA_ASSETS = ["EUR/USD", "XAU/USD"]

# VWAP cálculo
def calculate_vwap(df):
    try:
        df['TP'] = (df['high'] + df['low'] + df['close']) / 3
        df['PV'] = df['TP'] * df['volume']
        vwap = df['PV'].sum() / df['volume'].sum()
        return vwap
    except Exception as e:
        logging.error(f"Erro ao calcular VWAP: {e}")
        return None

# Supabase upsert
def upsert_ativo(nome, preco, vwap, sinal):
    payload = {
        "nome": nome,
        "preco": preco,
        "vwap": vwap,
        "sinal": sinal,
        "atualizado_em": datetime.utcnow().isoformat()
    }
    try:
        supabase.table("ativos").upsert(payload, on_conflict="nome").execute()
    except Exception as e:
        logging.error(f"Erro ao upsertar no Supabase para {nome}: {e}")

# Busca candles Coinbase (BTCUSD, ETHUSD)
def fetch_coinbase_candles(symbol, granularity=120):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={granularity}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        # Coinbase retorna lista: [time, low, high, open, close, volume]
        df = pd.DataFrame(data, columns=['time','low','high','open','close','volume'])
        df = df[['open','high','low','close','volume']]
        df = df.astype(float)
        return df
    except Exception as e:
        logging.warning(f"Falha ao buscar candles Coinbase {symbol}: {e}")
        return None

# Busca candles TwelveData (EURUSD, XAUUSD)
def fetch_twelvedata_candles(symbol, interval="2min", outputsize=100):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={TWELVEDATA_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "values" not in data:
            logging.warning(f"TwelveData retornou sem 'values' para {symbol}: {data}")
            return None
        df = pd.DataFrame(data["values"])
        df = df[['open','high','low','close','volume']].astype(float)
        return df
    except Exception as e:
        logging.warning(f"Erro ao buscar candles TwelveData {symbol}: {e}")
        return None

# Define sinal baseado no VWAP
def generate_signal(preco, vwap):
    if preco is None or vwap is None:
        return "NEUTRO"
    if preco > vwap:
        return "BUY"
    elif preco < vwap:
        return "SELL"
    else:
        return "NEUTRO"

# Processa todos ativos
def process_assets():
    while True:
        # Coinbase
        for symbol in COINBASE_ASSETS:
            df = fetch_coinbase_candles(symbol)
            if df is not None and not df.empty:
                vwap = calculate_vwap(df)
                preco = df['close'].iloc[-1]
                sinal = generate_signal(preco, vwap)
                upsert_ativo(symbol, preco, vwap, sinal)
                logging.info(f"{symbol} -> sinal={sinal} preco={preco:.2f} vwap={vwap:.2f}")
            else:
                logging.info(f"{symbol} -> sinal=NEUTRO preco=None vwap=None")

        # TwelveData
        for symbol in TWELVEDATA_ASSETS:
            df = fetch_twelvedata_candles(symbol)
            if df is not None and not df.empty:
                vwap = calculate_vwap(df)
                preco = df['close'].iloc[0]  # Último valor mais recente
                sinal = generate_signal(preco, vwap)
                upsert_ativo(symbol, preco, vwap, sinal)
                logging.info(f"{symbol} -> sinal={sinal} preco={preco:.2f} vwap={vwap:.2f}")
            else:
                logging.info(f"{symbol} -> sinal=NEUTRO preco=None vwap=None")

        time.sleep(REFRESH_INTERVAL)

# Função de inicialização
def start_bot():
    logging.info(f"Iniciando VWAP Monitor (Coinbase + TwelveData). Assets: {COINBASE_ASSETS + TWELVEDATA_ASSETS}")
    Thread(target=process_assets, daemon=True).start()
