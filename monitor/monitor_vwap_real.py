"""
Fetch data with yfinance and compute VWAP + bands and simple crossing signals.
Designed for: BTC-USD, ETH-USD, EURUSD=X, XAUUSD=X, WINZ25.SA (mini-índice dynamic ticker)
Timeframe: 15m (configurable when requesting chart data)
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime


# Default assets and tickers (you can change in repo later)
ASSETS = {
'BTCUSD': 'BTC-USD',
'ETHUSD': 'ETH-USD',
'EURUSD': 'EURUSD=X',
'XAUUSD': 'XAUUSD=X',
'WINZ25': 'WINZ25.SA'
}


# number of candles used to compute rolling metrics (we fetch period='1d' by default for 15m intervals)
CANDLES_TO_FETCH = 96 # ~24 hours with 15m candles




def _fetch_candles(ticker: str, period: str = '1d', interval: str = '15m') -> pd.DataFrame:
"""Return price dataframe with columns: Open, High, Low, Close, Volume and index as UTC datetime."""
try:
tk = yf.Ticker(ticker)
df = tk.history(period=period, interval=interval, prepost=False)
# yfinance may return empty; handle it
if df is None or df.empty:
return pd.DataFrame()
# ensure required columns
df = df[['Open','High','Low','Close','Volume']].dropna()
return df
except Exception as e:
return pd.DataFrame()




def compute_vwap_and_bands(df: pd.DataFrame, band_std_factor: float = 1.5) -> pd.DataFrame:
"""Compute VWAP and upper/lower bands based on rolling std of typical price."""
if df.empty:
return df
tp = (df['High'] + df['Low'] + df['Close']) / 3.0
df = df.copy()
df['typ_price'] = tp
df['pv'] = df['typ_price'] * df['Volume']
df['cum_pv'] = df['pv'].cumsum()
df['cum_vol'] = df['Volume'].cumsum().replace(0, np.nan)
df['vwap'] = (df['cum_pv'] / df['cum_vol']).ffill()
# rolling std of typical price
df['tp_std'] = df['typ_price'].rolling(window=20, min_periods=1).std().fillna(0)
df['upper'] = df['vwap'] + band_std_factor * df['tp_std']
df['lower'] = df['vwap'] - band_std_factor * df['tp_std']
return df




def detect_signal(df: pd.DataFrame) -> dict:
"""Detect a simple crossing signal on the last candle vs vwap.
BUY: last close > last vwap and prev close <= prev vwap
SELL: last close < last vwap and prev close >= prev vwap
NEUTRAL otherwise
Returns dict with 'signal' and 'signal_time' (ISO) and 'signal_price'.
"""
if df.empty or len(df) < 2:
return {'signal': 'NO_DATA', 'signal_time': None, 'signal_price': None}
last = df.iloc[-1]
prev = df.iloc[-2]
if (last['Close'] > last['vwap']) and (prev['Close'] <= prev['vwap']):
return {'signal': 'BUY', 'signal_time': last.name.isoformat(), 'signal_price': float(last['Close'])}
if (last['Close'] < last['vwap']) and (prev['Close'] >= prev['vwap']):
return {'signal': 'SELL', 'signal_time': last.name.isoformat(), 'signal_price': float(last['Close'])}
return {'signal': 'NEUTRAL', 'signal_time': None, 'signal_price': None}
}
