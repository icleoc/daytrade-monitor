import yfinance as yf
import pandas as pd
import time
from datetime import datetime

ASSETS = {
    "Índice Futuro": "WIN1!",
    "Ouro": "GC=F",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Euro": "EURUSD=X"
}

INTERVAL = "1m"  # 1 minuto
PERIOD = "7d"    # últimos 7 dias
RETRY = 3        # tentativas em caso de erro

def fetch_data(symbol):
    for attempt in range(RETRY):
        try:
            df = yf.download(symbol, interval=INTERVAL, period=PERIOD, progress=False, threads=True)
            if not df.empty:
                return df
        except Exception as e:
            print(f"Tentativa {attempt+1} falhou para {symbol}: {e}")
        time.sleep(1)
    print(f"Falha ao baixar dados de {symbol}")
    return pd.DataFrame()

def calculate_vwap(df):
    if df.empty:
        return df
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    return df

def get_all_data():
    data = {}
    for name, symbol in ASSETS.items():
        df = fetch_data(symbol)
        df = calculate_vwap(df)
        data[name] = df
    return data

if __name__ == "__main__":
    all_data = get_all_data()
    for name, df in all_data.items():
        if not df.empty:
            print(f"{name} último preço: {df['Close'].iloc[-1]:.2f}, VWAP: {df['VWAP'].iloc[-1]:.2f}")
        else:
            print(f"{name} sem dados")
