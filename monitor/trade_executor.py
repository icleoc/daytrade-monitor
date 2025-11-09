import requests
import os

def execute_trade(signal: str, quantity: float, asset: str):
    api_url = os.getenv("TRADING_API_URL")
    payload = {"signal": signal, "quantity": quantity, "asset": asset}
    resp = requests.post(api_url, json=payload)
    return resp.json()
