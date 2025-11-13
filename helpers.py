"""
helpers.py
Responsável por consultar TwelveData via REST, montar candles, calcular VWAP, bandas e sinais.
Design decisions:
- Usa TwelveData REST (sem dependências adicionais) para Forex e Commodities e CRYPTO.
- Faz mapeamento de símbolos: BTC/USDT -> BTC/USD (TwelveData usa USD base).
- Implementa cache simples em memória para evitar exceder rate limits (1 requisição/min por símbolo).
- Retorna estruturas JSON-serializáveis.
"""


import os
import time
import requests
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('helpers')


TWELVE_API_KEY = os.environ.get(config.TWELVE_API_ENV)


# simples cache em memória: {symbol: {'ts': epoch, 'data': payload}}
_cache = {}
_cache_ttl = config.UPDATE_INTERVAL_SECONDS - 0 if config.UPDATE_INTERVAL_SECONDS > 5 else 1


# Mapagem para TwelveData: usamos pares com USD. Recebe por ex 'BTC/USDT' -> 'BTC/USD'
_symbol_map = {
'BTC/USDT': 'BTC/USD',
'ETH/USDT': 'ETH/USD',
'EUR/USD': 'EUR/USD',
'XAU/USD': 'XAU/USD'
}


# TwelveData espera interval como '15min' (não '15m')
def _normalize_interval(tf):
mapping = {
'1m': '1min', '5m': '5min', '15m': '15min', '30m': '30min', '45m': '45min',
'1h': '1h', '2h': '2h', '4h': '4h', '8h': '8h', '1d': '1day'
}
return mapping.get(tf, tf)




def _twelve_time_series(symbol, interval='15min', outputsize=200):
"""Consulta TwelveData /time_series e retorna DataFrame com colunas: datetime, open, high, low, close, volume"""
global TWELVE_API_KEY
if not TWELVE_API_KEY:
raise RuntimeError('TWELVE_API_KEY ausente nas variáveis de ambiente')


td_symbol = _symbol_map.get(symbol, symbol)
interval_td = _normalize_interval(interval)


url = 'https://api.twelvedata.com/time_series'
params = {
'symbol': td_symbol,
'interval': interval_td,
'outputsize': outputsize,
'format': 'JSON',
'apikey': TWELVE_API_KEY
return out
