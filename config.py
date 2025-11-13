# Simple config module
import os


SYMBOLS = [
{"id": "BTCUSD", "td_symbol": "BTC/USD", "display": "BTC/USD", "type": "crypto"},
{"id": "ETHUSD", "td_symbol": "ETH/USD", "display": "ETH/USD", "type": "crypto"},
{"id": "EURUSD", "td_symbol": "EUR/USD", "display": "EUR/USD", "type": "forex"},
{"id": "XAUUSD", "td_symbol": "XAU/USD", "display": "XAU/USD", "type": "forex"},
]


# timeframe in minutes for candles
TIMEFRAME_MINUTES = int(os.getenv('TIMEFRAME_MINUTES', 15))
# how often front-end should poll (seconds)
UPDATE_INTERVAL_SECONDS = int(os.getenv('UPDATE_INTERVAL_SECONDS', 60))


# VWAP band multiplier (std dev)
VWAP_BAND_MULT = float(os.getenv('VWAP_BAND_MULT', 1.0))


TWELVE_API_KEY = os.getenv('TWELVE_API_KEY')
DEBUG = bool(int(os.getenv('DEBUG', '0')))
