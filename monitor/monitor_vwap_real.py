import requests
import yfinance as yf
from datetime import datetime
import pandas as pd

# === Configurações ===
TWELVE_API_KEY = "34b1f0bac586484c97725bbbbddad099"

# === Funções para buscar dados reais ===
def get_coinbase_price(symbol: str):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/ticker"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        return float(data.get("price", 0))
    except Exception:
        return None

def get_twelvedata_price(symbol: str):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_API_KEY}"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        return float(data.get("price", 0))
    except Exception:
        return None

def get_yfinance_price(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return float(data["Close"].iloc[-1])
        return None
    except Exception:
        return None

# === VWAP simplificado (com dados gratuitos) ===
def calculate_vwap(prices):
    if not prices:
        return None
    df = pd.DataFrame(prices, columns=["price"])
    df["volume"] = 1
    df["cum_vol"] = df["volume"].cumsum()
    df["cum_vol_price"] = (df["price"] * df["volume"]).cumsum()
    vwap = (df["cum_vol_price"] / df["cum_vol"]).iloc[-1]
    return round(float(vwap), 4)

# === Geração de sinal de compra/venda ===
def generate_signal(price, vwap, threshold=0.001):
    if not price or not vwap:
        return "Sem dados"
    diff = (price - vwap) / vwap
    if diff > threshold:
        return "📈 Compra"
    elif diff < -threshold:
        return "📉 Venda"
    return "⚖️ Neutro"

# === Função principal ===
def get_all_assets_data():
    assets = {
        "BTCUSD": get_coinbase_price("BTC-USD"),
        "ETHUSD": get_coinbase_price("ETH-USD"),
        "XAUUSD": get_twelvedata_price("XAU/USD"),
        "EURUSD": get_twelvedata_price("EUR/USD"),
        "WINZ25": get_yfinance_price("WIN=F")
    }

    result = {}
    for symbol, price in assets.items():
        if price:
            vwap = calculate_vwap([price])
            signal = generate_signal(price, vwap)
            result[symbol] = {
                "price": price,
                "vwap": vwap,
                "signal": signal,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            result[symbol] = {
                "price": None,
                "vwap": None,
                "signal": "Sem dados",
                "timestamp": datetime.utcnow().isoformat()
            }
    return result
