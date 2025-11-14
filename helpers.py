import os
closes = []
for c in candles:
typical = (c['h'] + c['l'] + c['c']) / 3.0
vol = c.get('v') or 0.0
# if volume missing, fallback to 1 to allow vwap to follow price
vol = vol if vol > 0 else 1.0
cum_pv += typical * vol
cum_v += vol
vwap = cum_pv / cum_v if cum_v != 0 else c['c']
vwap_list.append(vwap)
closes.append(c['c'])
# compute rolling stddev of price for bands
import math
bands = []
for i in range(len(candles)):
window = closes[max(0, i-19):i+1] # 20-period std
mean = sum(window) / len(window)
variance = sum((x-mean)**2 for x in window) / len(window)
sd = math.sqrt(variance)
upper = vwap_list[i] + band_mult * sd
lower = vwap_list[i] - band_mult * sd
bands.append({"vwap": vwap_list[i], "upper": upper, "lower": lower})
return bands


# Determine signal based on last close vs vwap
def determine_signal(candles, bands):
if not candles or not bands:
return "HOLD"
last = candles[-1]['c']
last_vwap = bands[-1]['vwap']
if last > last_vwap:
return "BUY"
elif last < last_vwap:
return "SELL"
else:
return "HOLD"


# Main orchestrator
def fetch_all_symbols(symbols, interval="15m"):
result = {}
for sym in symbols:
try:
logger.info(f"Fetching {sym} ({interval})")
if sym.endswith("/USDT"):
candles = fetch_crypto_yahoo(sym, interval=interval)
else:
# EUR/USD and XAU/USD via Twelve Data
candles = fetch_twelvedata(sym.replace('/', '/'), interval=interval)
if not candles:
result[sym] = {"error": "Sem dados", "symbol": sym}
continue
# compute bands
bands = compute_vwap_and_bands(candles)
signal = determine_signal(candles, bands)
# Prepare JSON serializable structure
result[sym] = {
"symbol": sym,
"candles": candles,
"bands": bands,
"signal": signal,
"last": candles[-1]['c']
}
except Exception as e:
logger.exception(f"Erro ao buscar {sym}: {e}")
result[sym] = {"error": str(e), "symbol": sym}
return result
