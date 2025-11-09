import time
import threading
import requests
from datetime import datetime, timezone
from supabase import create_client, Client

# ======================
# CONFIGURAÇÃO
# ======================

# Supabase
SUPABASE_URL = "https://<SEU-PROJETO>.supabase.co"  # substitua
SUPABASE_KEY = "<SUA-CHAVE>"  # substitua
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Coinbase
COINBASE_ASSETS = ["BTC-USD", "ETH-USD"]
COINBASE_GRANULARITY = 60  # 1 minuto em segundos

# TwelveData
TWELVEDATA_ASSETS = ["EUR/USD", "XAU/USD"]
TWELVEDATA_INTERVAL = "1min"  # intervalo válido
TWELVEDATA_API_KEY = "<SUA_CHAVE_TWELVEDATA>"  # substitua

# Loop de atualização em segundos
UPDATE_INTERVAL = 60

# ======================
# FUNÇÕES DE SUPORTE
# ======================

def fetch_coinbase_candles(symbol: str):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={COINBASE_GRANULARITY}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Falha ao buscar candles Coinbase {symbol}: {e}")
        return None

def fetch_twelvedata_candles(symbol: str):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={TWELVEDATA_INTERVAL}&apikey={TWELVEDATA_API_KEY}&outputsize=1"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "values" in data and len(data["values"]) > 0:
            return data["values"]
        else:
            print(f"TwelveData retornou sem 'values' para {symbol}: {data}")
            return None
    except Exception as e:
        print(f"Falha ao buscar candles TwelveData {symbol}: {e}")
        return None

def calculate_vwap(candles):
    if not candles:
        return None
    total_volume = 0
    total_vwap = 0
    for c in candles:
        if isinstance(c, list):  # Coinbase: [time, low, high, open, close, volume]
            price = float(c[4])
            volume = float(c[5])
        elif isinstance(c, dict):  # TwelveData: dict
            price = float(c["close"])
            volume = float(c.get("volume", 1))
        else:
            continue
        total_vwap += price * volume
        total_volume += volume
    if total_volume == 0:
        return None
    return total_vwap / total_volume

def determine_signal(price, vwap):
    if price is None or vwap is None:
        return "NEUTRO"
    if price > vwap:
        return "COMPRA"
    elif price < vwap:
        return "VENDA"
    else:
        return "NEUTRO"

def upsert_ativo(nome, preco, vwap, sinal):
    payload = {
        "nome": nome,
        "preco": preco,
        "vwap": vwap,
        "sinal": sinal,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    try:
        supabase.table("ativos").upsert(payload, on_conflict="nome").execute()
    except Exception as e:
        print(f"Erro ao upsertar no Supabase para {nome}: {e}")

# ======================
# LOOP PRINCIPAL
# ======================

def monitor_loop():
    while True:
        # Coinbase
        for asset in COINBASE_ASSETS:
            candles = fetch_coinbase_candles(asset)
            vwap = calculate_vwap(candles)
            price = float(candles[-1][4]) if candles else None
            signal = determine_signal(price, vwap)
            upsert_ativo(asset, price, vwap, signal)
            print(f"{asset} -> sinal={signal} preco={price} vwap={vwap}")

        # TwelveData
        for asset in TWELVEDATA_ASSETS:
            candles = fetch_twelvedata_candles(asset)
            vwap = calculate_vwap(candles)
            price = float(candles[0]["close"]) if candles else None
            signal = determine_signal(price, vwap)
            upsert_ativo(asset, price, vwap, signal)
            print(f"{asset} -> sinal={signal} preco={price} vwap={vwap}")

        time.sleep(UPDATE_INTERVAL)

def start_background_thread():
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()

# ======================
# EXECUÇÃO AUTOMÁTICA
# ======================
if __name__ == "__main__":
    print("Iniciando VWAP Monitor (Coinbase + TwelveData)")
    start_background_thread()
    # Mantém o script vivo
    while True:
        time.sleep(1)
