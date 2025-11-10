import yfinance as yf
import pandas as pd

# Tickers ajustados para contratos contínuos ou ativos relevantes
ASSETS = [
    '^BVSP',       # Índice futuro contínuo
    'USDBRL=X',    # Dólar
    # Adicione outros ativos se necessário
]

def get_assets_data(assets=ASSETS, interval='15m', period='7d'):
    all_data = {}
    for symbol in assets:
        try:
            df = yf.download(symbol, interval=interval, period=period, progress=False)
            if df.empty:
                print(f"Aviso: ticker '{symbol}' não retornou dados")
            all_data[symbol] = df
        except Exception as e:
            print(f"Falha ao obter ticker '{symbol}': {e}")
            all_data[symbol] = pd.DataFrame()  # evita erro no dashboard
    return all_data
