"""Helpers to fetch OHLC data and compute VWAP and signals.
Primary source: Twelve Data (requires TWELVE_API_KEY). Fallback: CoinGecko for BTC/ETH only.
"""
import time
import logging
import os
from typing import List, Dict, Any
import requests
import pandas as pd
import numpy as np
from config import TWELVE_API_KEY, TIMEFRAME_MINUTES, VWAP_BAND_MULT


logger = logging.getLogger('helpers')
logger.setLevel(logging.INFO)


# --- Utilities ---


def _to_unix_ms(ts):
return int(int(ts) / 1000) if ts > 1e12 else int(ts * 1000)


# --- Fetchers ---


def fetch_from_twelvedata(symbol: str, interval: str = '15min', outputsize: int = 500) -> pd.DataFrame:
"""Fetch time_series from Twelve Data. Returns DataFrame with columns: datetime, open, high, low, close, volume"""
if not TWELVE_API_KEY:
raise RuntimeError('TWELVE_API_KEY missing')


url = 'https://api.twelvedata.com/time_series'
params = {
'symbol': symbol,
'interval': interval,
'outputsize': outputsize,
'format': 'JSON',
'apikey': TWELVE_API_KEY,
}
resp = requests.get(url, params=params, timeout=15)
resp.raise_for_status()
data = resp.json()


if 'values' not in data:
raise RuntimeError(f'Unexpected Twelve Data response: {data.get("message") or data}')


df = pd.DataFrame(data['values'])
# Twelve Data returns newest first; reverse
df = df.iloc[::-1].reset_index(drop=True)
# ensure correct types
df['datetime'] = pd.to_datetime(df['datetime'])
df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
if 'volume' in df.columns:
df['volume'] = df['volume'].astype(float)
else:
df['volume'] = 0.0
return df




def fetch_from_coingecko(symbol_id: str, vs_currency: str = 'usd', minutes: int = 15, points: int = 500) -> pd.DataFrame:
"""Fetch OHLC-like data via CoinGecko (ohlc endpoint). symbol_id: 'bitcoin' or 'ethereum'
Returns timestamp in ms.
"""
return out
