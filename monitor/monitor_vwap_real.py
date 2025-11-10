import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_assets_data(assets, interval='15m', period='7d'):
    all_data = {}
    for symbol in assets:
        df = yf.download(symbol, interval=interval, period=period, progress=False)
        df = df.dropna()
        df['vwap'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        df['vwap_std'] = df['Close'].rolling(20).std()
        df['vwap_upper'] = df['vwap'] + df['vwap_std']
        df['vwap_lower'] = df['vwap'] - df['vwap_std']

        # gerar sinais simples (exemplo)
        df['signal'] = np.where(df['Close'] > df['vwap_upper'], 'sell',
                                np.where(df['Close'] < df['vwap_lower'], 'buy', ''))

        signals = df[df['signal'] != ''][['Close', 'signal']]
        signals = signals.rename(columns={'Close':'price'})
        signals['datetime'] = signals.index

        all_data[symbol] = {'df': df, 'signals': signals}

    return all_data
