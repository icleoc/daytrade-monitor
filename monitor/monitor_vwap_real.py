import yfinance as yf
import pandas as pd

def get_assets_data(symbols, interval='15m', period='7d'):
    all_data = {}
    for symbol in symbols:
        try:
            df = yf.download(symbol, interval=interval, period=period, progress=False)
            if not df.empty:
                all_data[symbol] = df
            else:
                print(f"Sem dados para {symbol}")
        except Exception as e:
            print(f"Falha ao obter ticker '{symbol}' reason: {e}")
    return all_data
