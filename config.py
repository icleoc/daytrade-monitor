# config.py
import os
from dotenv import load_dotenv

# Load .env in local dev
load_dotenv()

# API keys
CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY", "7d87c8a694a1b0d2febdbe38a7428157c2be6c22c82fd47c3fd3e399f9a2bf40")

# Symbols to monitor (must match frontend)
SYMBOLS = ["BTCUSD", "ETHUSD", "EURUSD", "XAUUSD"]

# Candle timeframe and limits
TIMEFRAME_MINUTES = 15   # timeframe requested (15m)
CANDLE_LIMIT = 400       # how many candles to fetch (enough history for VWAP)
UPDATE_INTERVAL_SECONDS = 60  # frontend poll interval

# VWAP bands params
BAND_STD_MULTIPLIER = 2.0

# Other
CRYPTOCOMPARE_BASE = "https://min-api.cryptocompare.com/data/v2"
# If you prefer another provider for EUR/XAU, we'll add later.
