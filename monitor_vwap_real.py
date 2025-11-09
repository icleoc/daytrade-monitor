import time
import threading
import requests
from datetime import datetime
from supabase import create_client, Client

# --- CONFIGURAÇÕES SUPABASE ---
SUPABASE_URL = "<sua-supabase-url>"
SUPABASE_KEY = "<sua-supabase-key>"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- PARES A SEREM MONITORADOS ---
ASSETS = ["BTC-USD", "ETH-USD", "EUR/USD", "XAU/USD"]

# --- INTERVALOS ---
COINBASE_GRANULARITY = 60  # 1 minuto em segundos
TWELVEDATA_INTERVAL = "1min"

# --- FUNÇÕES DE FETCH ---

def fetch_coinbase_candles(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles"
    params = {"granularity": COINBASE_GRANULARITY}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        # data = [[time, low, high, open, close, volume], ...]
        close_prices = [c[4] for c in data]
        return close_prices
    except Exception as e:
        print(f"[WARNING] Falha ao buscar candles Coinbase {symbol}: {e}")
        return None

def fetch_twelvedata_candles(symbol):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": TWELVEDATA_INTERVAL,
        "apikey": "<sua-twelvedata-key>",
        "outputsize": 500
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "values" not in data or not data["values"]:
            return None
        close_prices = [float(c["close"]) for c in reversed(data["values"])]
        return close_prices
    except Exception as e:
        print(f"[WARNING] TwelveData retornou sem 'values' para {symbol}: {e}")
        return None

# --- CÁLCULO DE VWAP SIMPLES ---

def calculate_vwap(prices):
    if not prices:
        return None
    vwap = sum(prices) / len(prices)
    return vwap

# --- FUNÇÃO DE UPLOAD PARA SUPABASE ---

def upsert_ativo(nome, preco, vwap, sinal):
    payload = {
        "nome": nome,
        "preco": preco,
        "vwap": vwap,
        "sinal": sinal,
        "updated_at": datetime.utcnow().isoformat()
    }
    try:
        supabase.table("ativos").upsert(payload, on_conflict="nome").execute()
    except Exception as e:
        print(f"[ERROR] Erro ao upsertar no Supabase para {nome}: {e}")

# --- LOOP PRINCIPAL ---

def monitor_loop():
    while True:
        for asset in ASSETS:
            if asset in ["BTC-USD", "ETH-USD"]:
                prices = fetch_coinbase_candles(asset)
            else:
                prices = fetch_twelvedata_candles(asset)
            
            if prices:
                vwap = calculate_vwap(prices)
                last_price = prices[-1]
                sinal = "NEUTRO"
                if last_price > vwap:
                    sinal = "COMPRA"
                elif last_price < vwap:
                    sinal = "VENDA"
            else:
                vwap = None
                last_price = None
                sinal = "NEUTRO"
            
            print(f"{asset} -> sinal={sinal} preco={last_price} vwap={vwap}")
            upsert_ativo(asset, last_price, vwap, sinal)
        
        # Aguarda 1 minuto para próximo ciclo
        time.sleep(60)

# --- THREAD DE BACKGROUND ---

def start_background_thread():
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()

# --- INICIO ---
if __name__ == "__main__":
    print(f"Iniciando VWAP Monitor (Coinbase + TwelveData). Assets: {ASSETS}")
    start_background_thread()
    # Mantém o script rodando
    while True:
        time.sleep(1)
