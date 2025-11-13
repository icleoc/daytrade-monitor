import os

# Símbolos que combinamos
SYMBOLS = ["BTCUSDT", "ETHUSDT", "EURUSD", "XAUUSD"]

# Atualização / cache
UPDATE_INTERVAL_SECONDS = 60  # 1 requisição por minuto (TTL do cache)

# VWAP / bands params
BAND_STD_MULTIPLIER = 1.0  # multiplicador para banda (pode ajustar)

# Twelve Data
TWELVE_API_KEY = os.getenv("TWELVE_API_KEY", "").strip()

# CoinGecko fallback config
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# Misc
MAX_CANDLES = 200  # máximo de candles a buscar/retornar

# config.py
TWELVE_API_KEY = "34b1f0bac586484c97725bbbbddad099"
