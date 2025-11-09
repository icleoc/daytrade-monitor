import threading
import time
import requests
from datetime import datetime, timezone

# Ativos que vamos monitorar
ASSETS = ["BTC-USD", "ETH-USD", "EUR/USD", "XAU/USD"]

# Cache em memória para sinais
cache_sinais = {asset: {"sinal": "NEUTRO", "preco": None, "vwap": None} for asset in ASSETS}

# Função fictícia de cálculo VWAP (substitua por real)
def calcular_vwap(candles):
    if not candles:
        return None
    total_volume = sum(c[5] for c in candles)
    if total_volume == 0:
        return None
    return sum(c[4]*c[5] for c in candles)/total_volume

# Função para buscar candles do Coinbase
def buscar_candles_coinbase(asset):
    if asset in ["BTC-USD", "ETH-USD"]:
        url = f"https://api.exchange.coinbase.com/products/{asset}/candles?granularity=300"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data  # Lista de candles
        except:
            return None
    return None

# Função para buscar candles do TwelveData (EUR/USD, XAU/USD)
TD_API_KEY = "SUA_CHAVE_TWELVEDATA"  # Substitua pela sua chave TwelveData
def buscar_candles_twelvedata(asset):
    if asset in ["EUR/USD", "XAU/USD"]:
        interval = "1min"
        url = f"https://api.twelvedata.com/time_series?symbol={asset}&interval={interval}&apikey={TD_API_KEY}&outputsize=10"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if "values" in data:
                candles = [
                    [v["datetime"], float(v["open"]), float(v["high"]), float(v["low"]), float(v["close"]), float(v["volume"])]
                    for v in reversed(data["values"])
                ]
                return candles
            return None
        except:
            return None
    return None

# Função para atualizar o cache
def atualizar_sinal(asset):
    if asset in ["BTC-USD", "ETH-USD"]:
        candles = buscar_candles_coinbase(asset)
    else:
        candles = buscar_candles_twelvedata(asset)
    
    if candles:
        vwap = calcular_vwap(candles)
        preco = candles[-1][4] if candles else None
        # Lógica simples de sinal
        sinal = "COMPRA" if preco and vwap and preco > vwap else "VENDA" if preco and vwap and preco < vwap else "NEUTRO"
        cache_sinais[asset] = {"sinal": sinal, "preco": preco, "vwap": vwap}
    else:
        cache_sinais[asset] = {"sinal": "NEUTRO", "preco": None, "vwap": None}

# Loop principal do monitor
def monitor_loop():
    while True:
        for asset in ASSETS:
            atualizar_sinal(asset)
        time.sleep(60)  # Atualiza a cada 60 segundos

# Função para iniciar thread em background
def start_background_thread():
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()

# Função para retornar sinais atuais (para Flask)
def get_current_signals():
    return cache_sinais
