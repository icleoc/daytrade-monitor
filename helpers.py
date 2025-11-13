import os
import pandas as pd
from twelve_data import TDClient  # supondo que você usa o pacote oficial
from datetime import datetime

API_KEY = os.getenv("TWELVE_API_KEY")
td = TDClient(apikey=API_KEY)

def get_all_data():
    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "XAUUSD"]
    result = {}
    
    for symbol in symbols:
        try:
            # Busca candles
            candles = td.time_series(symbol=symbol, interval="15min", outputsize=100).as_pandas()
            
            # Calcula VWAP e bandas
            candles['vwap'] = (candles['close'] * candles['volume']).cumsum() / candles['volume'].cumsum()
            candles['upper_band'] = candles['vwap'] + candles['vwap'].rolling(20).std()
            candles['lower_band'] = candles['vwap'] - candles['vwap'].rolling(20).std()
            
            # Sinais de compra/venda
            signals = []
            for idx, row in candles.iterrows():
                if row['close'] > row['upper_band']:
                    signals.append({"datetime": idx.isoformat(), "signal": "SELL", "price": row['close']})
                elif row['close'] < row['lower_band']:
                    signals.append({"datetime": idx.isoformat(), "signal": "BUY", "price": row['close']})
            
            # Serializa candles para frontend
            df_serialized = candles.reset_index()[['datetime','open','high','low','close','vwap','upper_band','lower_band']].to_dict(orient='records')
            
            result[symbol] = {
                "last": candles['close'].iloc[-1],
                "signals": signals,
                "df": df_serialized,
                "error": None
            }
            
        except Exception as e:
            result[symbol] = {
                "last": None,
                "signals": [],
                "df": [],
                "error": str(e)
            }
    
    return result
