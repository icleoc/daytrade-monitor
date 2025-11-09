# monitor_vwap_real.py
import os
import time
import requests
import pandas as pd
from datetime import datetime, timezone
from supabase import create_client, Client

# Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TWELVE_KEY = os.getenv("TWELVE_API_KEY")
ASSETS_RAW = os.getenv("ASSETS", "BTCUSDT:binance,XAUUSD:twelvedata").strip()
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "120"))  # 2 minutes

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL e SUPABASE_KEY precisam estar configuradas nas variáveis de ambiente.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Parse assets: "BTCUSDT:binance,EURUSD:twelvedata"
ASSETS = []
for token in ASSETS_RAW.split(","):
    token = token.strip()
    if not token: continue
    if ":" in token:
        sym, source = token.split(":", 1)
    else:
        sym, source = token, "binance"
    ASSETS.append({"symbol": sym.strip(), "source": source.strip().lower()})

# Helpers: Binance candlesticks
def fetch_binance_klines(symbol: str, interval: str = "2m", limit: int = 20):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    # each kline: [openTime, open, high, low, close, volume, closeTime, ...]
    df = pd.DataFrame(data, columns=[
        "open_time","open","high","low","close","volume","close_time","qav","num_trades","taker_base","taker_quote","ignore"
    ])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    return df

# Helpers: Twelve Data time_series
def fetch_twelvedata_series(symbol: str, interval: str = "2min", outputsize: int = 20):
    # symbol examples: "XAU/USD" or "EUR/USD" (Twelve Data expects XAU/USD)
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "format": "JSON",
        "apikey": TWELVE_KEY
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    j = r.json()
    if "values" not in j:
        raise RuntimeError(f"TwelveData error for {symbol}: {j}")
    vals = j["values"]
    df = pd.DataFrame(vals)
    # values come as strings: datetime, open, high, low, close, volume (volume may be null)
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    if "volume" in df.columns:
        # some symbols may return volume as empty strings
        try:
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0.0)
        except:
            df["volume"] = 0.0
    else:
        df["volume"] = 0.0
    return df[::-1].reset_index(drop=True)  # reverse to chronological

# VWAP calculation (uses volume if >0; otherwise fallback to typical price SMA)
def compute_vwap_from_df(df: pd.DataFrame):
    # df expected columns: high, low, close, volume
    # typical price
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    vol = df["volume"]
    if vol.sum() > 0:
        vwap = (tp * vol).sum() / vol.sum()
        return float(vwap)
    else:
        # fallback to simple moving average of typical price
        return float(tp.mean())

# Decide signal
def decide_signal(price: float, vwap: float, threshold_pct=0.0015):
    # threshold_pct: 0.15% default -> small hysteresis zone to avoid noise
    if price < vwap * (1 - threshold_pct):
        return "COMPRA"
    elif price > vwap * (1 + threshold_pct):
        return "VENDA"
    else:
        return "NEUTRO"

# Probability rough measure
def estimate_confidence(price: float, vwap: float):
    diff = abs(price - vwap) / vwap
    prob = min(round(diff * 300 * 100, 2), 99.0)  # scaled heuristic, cap 99%
    # Actually diff*100 gives %, multiply factor adjusts sensitivity
    return prob

# Save signal
def save_signal(asset, source, signal, price, vwap, prob):
    try:
        row = {
            "ativo": asset,
            "fonte": source,
            "sinal": signal,
            "preco": float(price),
            "vwap": float(vwap),
            "probabilidade": float(prob),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        supabase.table(os.getenv("SUPABASE_TABLE_SIGNALS", "sinais_vwap")).insert(row).execute()
        print(f"[{asset}] {signal} @ {price} (vwap={vwap}) prob={prob}%")
    except Exception as e:
        print("Erro ao salvar sinal:", e)

# Main loop (single round)
def process_round():
    for a in ASSETS:
        sym = a["symbol"]
        src = a["source"]
        try:
            if src == "binance":
                df = fetch_binance_klines(sym, interval="2m", limit=20)
                # use last close as current price
                price = float(df["close"].iloc[-1])
                vwap = compute_vwap_from_df(df)
            elif src in ("twelvedata", "twelvedata_raw", "twelvedata_api", "twelvedata_api_v1", "twelvedata"):
                # Twelve Data expects symbol like "XAU/USD" or "EUR/USD"
                df = fetch_twelvedata_series(sym, interval="2min", outputsize=20)
                price = float(df["close"].iloc[-1])
                vwap = compute_vwap_from_df(df)
            else:
                print("Fonte desconhecida:", src)
                continue

            signal = decide_signal(price, vwap, threshold_pct=0.0015)  # 0.15%
            prob = estimate_confidence(price, vwap) if signal != "NEUTRO" else 0.0

            if signal != "NEUTRO":
                save_signal(sym, src, signal, price, vwap, prob)
            else:
                # Optionally save neutral too (comment out if not desired)
                save_signal(sym, src, signal, price, vwap, prob)

        except Exception as e:
            print(f"Erro processando {sym} ({src}): {e}")

# Runner
if __name__ == "__main__":
    print("Iniciando monitor VWAP real. Assets:", ASSETS)
    while True:
        try:
            process_round()
        except Exception as e:
            print("Erro geral no round:", e)
        time.sleep(POLL_INTERVAL)
