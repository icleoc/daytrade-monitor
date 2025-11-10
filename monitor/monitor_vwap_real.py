import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

TICKERS = ['WIN$N', 'EURUSD=X', 'GC=F']  # Mini-índice, Forex, Ouro
INTERVAL = '15m'
CANDLE_COUNT = 50  # ajuste automático se necessário

def calculate_vwap(df):
    vwap = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    std = df['Close'].rolling(20).std()
    upper = vwap + std
    lower = vwap - std
    return vwap, upper, lower

def get_signals(df, vwap):
    signals = []
    if df.empty: return signals
    if df['Close'].iloc[-1] > vwap.iloc[-1]:
        signals.append({'time': df.index[-1].timestamp()*1000, 'price': df['Close'].iloc[-1], 'type':'Compra'})
    elif df['Close'].iloc[-1] < vwap.iloc[-1]:
        signals.append({'time': df.index[-1].timestamp()*1000, 'price': df['Close'].iloc[-1], 'type':'Venda'})
    return signals

def get_assets_data():
    assets = []
    for ticker in TICKERS:
        df = yf.download(ticker, period='2d', interval=INTERVAL, progress=False)
        if df.empty: continue

        vwap, upper, lower = calculate_vwap(df)

        candles = [
            {'time': int(idx.timestamp()*1000), 'open': row['Open'], 'high': row['High'], 'low': row['Low'], 'close': row['Close']}
            for idx, row in df.iterrows()
        ]
        vwap_data = [{'time': int(idx.timestamp()*1000), 'value': val} for idx, val in vwap.iteritems()]
        upper_band = [{'time': int(idx.timestamp()*1000), 'value': val} for idx, val in upper.iteritems()]
        lower_band = [{'time': int(idx.timestamp()*1000), 'value': val} for idx, val in lower.iteritems()]
        signals = get_signals(df, vwap)

        asset_data = {
            'ticker': ticker,
            'price': df['Close'].iloc[-1],
            'vwap': round(vwap.iloc[-1],2),
            'candles': candles,
            'vwapData': vwap_data,
            'upperBand': upper_band,
            'lowerBand': lower_band,
            'signals': signals,
            'signal': signals[-1]['type'] if signals else None
        }
        assets.append(asset_data)
    return assets
