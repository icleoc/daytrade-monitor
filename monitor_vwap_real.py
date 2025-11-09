import threading
import time
import os
import requests

current_signals = {}

# Definindo os ativos
ASSETS_COINBASE = ["BTC-USD", "ETH-USD"]
ASSETS_TWELVEDATA = ["EUR/USD", "XAU/USD"]

TWELVEDATA_API_KEY = os.environ.get("TWELVEDATA_API_KEY")
COINBASE_GRANULARITY = int(os.environ.get("COINBASE_GRANULARITY", 60))
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 10))

# Função para buscar dados da Coinbase
def fetch_coinbase(asset):
    url = f"https://api.exchange.coinbase.com/products/{asset}/candles?granularity={COINBASE_GRANULARITY}"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        if not data:
            return {"preco": None, "vwap": None, "sinal": "NEUTRO"}
        # Coinbase retorna [time, low, high, open, close, volume]
        close_prices = [c[4] for c in data]
        preco = close_prices[-1]
        vwap = sum([(c[1]+c[2]+c[4])/3*c[5] for c in data]) / sum([c[5] for c in data])
        sinal = "COMPRA" if preco > vwap else "VENDA" if preco < vwap else "NEUTRO"
        return {"preco": preco, "vwap": vwap, "sinal": sinal}
    except Exception as e:
        return {"preco": None, "vwap": None, "sinal": "NEUTRO"}

# Função para buscar dados da TwelveData
def fetch_twelvedata(asset):
    interval = "1min"
    symbol = asset.replace("/", "")
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={TWELVEDATA_API_KEY}&outputsize=20"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        if "values" not in data:
            return {"preco": None, "vwap": None, "sinal": "NEUTRO"}
        close_prices = [float(v["close"]) for v in data["values"]]
        volume = [float(v["volume"]) for v in data["values"]]
        preco = close_prices[0]
        vwap = sum([p*v for p,v in zip(close_prices, volume)])/sum(volume) if sum(volume) > 0 else preco
        sinal = "COMPRA" if preco > vwap else "VENDA" if preco < vwap else "NEUTRO"
        return {"preco": preco, "vwap": vwap, "sinal": sinal}
    except Exception as e:
        return {"preco": None, "vwap": None, "sinal": "NEUTRO"}

# Loop principal do monitoramento
def monitor_loop():
    while True:
        for asset in ASSETS_COINBASE:
            current_signals[asset] = fetch_coinbase(asset)
        for asset in ASSETS_TWELVEDATA:
            current_signals[asset] = fetch_twelvedata(asset)
        time.sleep(POLL_INTERVAL)

# Inicia thread de background
def start_background_thread():
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
