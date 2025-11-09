import os
import time
import requests
import pandas as pd
from datetime import datetime, timezone
from supabase import create_client, Client

# ----------------------------
# Configurações e API Keys
# ----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

COINBASE_ASSETS = ["BTC-USD", "ETH-USD"]
TWELVEDATA_ASSETS = ["EUR/USD", "XAU/USD"]
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 30))  # segundos

# ----------------------------
# Logs de sinais
# ----------------------------
signal_log = {}  # Último sinal de cada ativo

def log_signal_change(symbol, price, vwap, signal):
    """
    Registra alteração de sinal. Só loga se houver mudança real.
    """
    last_signal = signal_log.get(symbol)
    if last_signal != signal:
        signal_log[symbol] = signal
        now_local = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        print(f"[{now_local}] {symbol} mudou para {signal} | preço={price} vwap={vwap}")

# ----------------------------
# Funções auxiliares
# ----------------------------
def upsert_supabase(nome, preco, vwap, sinal):
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
        print(f"Erro ao upsertar no Supabase para {nome}: {e}")

def fetch_coinbase_candles(symbol):
    """Busca candles de 2 minutos na Coinbase"""
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity=120"
    headers = {"User-Agent": "VWAP-Monitor"}
    resp = requests.get(url, headers=headers, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    df = pd.DataFrame(data, columns=["time","low","high","open","close","volume"])
    df = df.sort_values("time")
    return df

def fetch_twelvedata_candles(symbol):
    """Busca candles de 2 minutos na TwelveData"""
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=2min&apikey={TWELVEDATA_API_KEY}&outputsize=100"
    resp = requests.get(url, timeout=5).json()
    if "values" not in resp:
        raise ValueError(f"Falha ao obter dados TwelveData: {resp}")
    df = pd.DataFrame(resp["values"])
    df = df.astype({"close":"float","volume":"float","high":"float","low":"float","open":"float"})
    df = df.sort_values("datetime")
    return df

def calculate_vwap(df):
    """Calcula VWAP do DataFrame"""
    if df.empty:
        return None
    vwap = (df["close"] * df["volume"]).sum() / df["volume"].sum()
    return round(vwap, 2)

def get_signal(price, vwap):
    if price is None or vwap is None:
        return "NEUTRO"
    if price > vwap:
        return "BUY"
    elif price < vwap:
        return "SELL"
    else:
        return "NEUTRO"

# ----------------------------
# Loop principal
# ----------------------------
def start_bot():
    print(f"Iniciando VWAP Monitor (Coinbase + TwelveData). Assets: {COINBASE_ASSETS + TWELVEDATA_ASSETS}")
    while True:
        try:
            for symbol in COINBASE_ASSETS:
                try:
                    df = fetch_coinbase_candles(symbol)
                    last_price = df["close"].iloc[-1]
                    vwap = calculate_vwap(df)
                    signal = get_signal(last_price, vwap)
                except Exception as e:
                    print(f"Falha ao buscar candles Coinbase {symbol}: {e}")
                    last_price, vwap, signal = None, None, "NEUTRO"

                upsert_supabase(symbol, last_price, vwap, signal)
                log_signal_change(symbol, last_price, vwap, signal)

            for symbol in TWELVEDATA_ASSETS:
                try:
                    df = fetch_twelvedata_candles(symbol)
                    last_price = df["close"].iloc[-1]
                    vwap = calculate_vwap(df)
                    signal = get_signal(last_price, vwap)
                except Exception as e:
                    print(f"Falha ao buscar candles TwelveData {symbol}: {e}")
                    last_price, vwap, signal = None, None, "NEUTRO"

                upsert_supabase(symbol, last_price, vwap, signal)
                log_signal_change(symbol, last_price, vwap, signal)

        except Exception as e:
            print(f"Erro geral no loop do bot: {e}")

        time.sleep(REFRESH_INTERVAL)
