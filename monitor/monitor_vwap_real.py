import requests
import os

COINBASE_URL = "https://api.coinbase.com/v2/prices"
TWELVE_URL = "https://api.twelvedata.com/price"
TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")

def get_coinbase_price(symbol):
    try:
        response = requests.get(f"{COINBASE_URL}/{symbol}/spot")
        return float(response.json()["data"]["amount"])
    except Exception as e:
        print(f"Erro Coinbase {symbol}: {e}")
        return None

def get_twelvedata_price(symbol):
    try:
        response = requests.get(f"{TWELVE_URL}?symbol={symbol}&apikey={TWELVE_API_KEY}")
        return float(response.json()["price"])
    except Exception as e:
        print(f"Erro TwelveData {symbol}: {e}")
        return None

def get_b3_price():
    try:
        response = requests.get("https://brapi.dev/api/quote/WINZ25")
        return float(response.json()["results"][0]["regularMarketPrice"])
    except Exception as e:
        print(f"Erro B3 WINZ25: {e}")
        return None

def calculate_vwap(prices):
    return round(sum(prices) / len(prices), 4) if prices else None

def get_all_vwap_data():
    assets = {
        "BTCUSD": get_coinbase_price("BTC-USD"),
        "ETHUSD": get_coinbase_price("ETH-USD"),
        "XAUUSD": get_twelvedata_price("XAU/USD"),
        "EURUSD": get_twelvedata_price("EUR/USD"),
        "WINZ25": get_b3_price()
    }

    vwap_results = {}
    for asset, price in assets.items():
        if price:
            vwap = calculate_vwap([price])
            signal = "COMPRA" if price < vwap else "VENDA" if price > vwap else "NEUTRO"
            vwap_results[asset] = {"price": price, "vwap": vwap, "signal": signal}
        else:
            vwap_results[asset] = {"error": "Sem dados"}

    return vwap_results
