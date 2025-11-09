# monitor_vwap.py
import os
import time
import requests
import pandas as pd
from datetime import datetime, timezone
from supabase import create_client, Client
from binance_client import fetch_binance_klines_df

# Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TWELVE_KEY = os.getenv("TWELVE_API_KEY")
ASSETS_RAW = os.getenv("ASSETS", "BTCUSDT:binance,ETHUSDT:binance,XAU/USD:twelvedata,EUR/USD:twelvedata")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "120"))
TABLE = os.getenv("SUPABASE_TABLE_SIGNALS", "sinais_vwap")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL e SUPABASE_KEY precisam estar configuradas nas env vars.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Parse assets
ASSETS = []
for token in ASSETS_RAW.split(","):
    token = token.strip()
    if not token:
        continue
    if ":" in token:
        sym, src = token.split(":", 1)
    else:
        sym, src = token, "binance"
    ASSETS.append({"symbol": sym.strip(), "source": src.strip().lower()})

# Twelve Data fetcher
def fetch_twelvedata_series(symbol: str, interval: str = "2min", outputsize: int = 100):
    if not TWELVE_KEY:
        raise RuntimeError("TWELVE_API_KEY não configurada.")
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "format": "JSON",
        "apikey": TWELVE_KEY
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    j = r.json()
    if "values" not in j:
        raise RuntimeError(f"TwelveData erro para {symbol}: {j}")
    vals = j["values"]
    df = pd.DataFrame(vals)
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0.0)
    else:
        df["volume"] = 0.0
    # values are in descending order — reverse to chronological
    df = df[::-1].reset_index(drop=True)
    # convert datetime if present
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])
    return df

# VWAP calc
def compute_vwap_from_df(df: pd.DataFrame):
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    vol = df["volume"]
    if vol.sum() > 0:
        vwap = (tp * vol).sum() / vol.sum()
        return float(vwap)
    else:
        # fallback: SMA of typical price
        return float(tp.mean())

# Decision logic
def decide_signal(price: float, vwap: float, threshold_pct=0.0015):
    # hysteresis to avoid noise (0.15%)
    if price < vwap * (1 - threshold_pct):
        return "COMPRA"
    elif price > vwap * (1 + threshold_pct):
        return "VENDA"
    else:
        return "NEUTRO"

def estimate_confidence(price: float, vwap: float):
    diff = abs(price - vwap) / vwap
    # scale to sensible %
    prob = min(round(diff * 100 * 10, 2), 99.0)  # heuristic
    return prob

def save_signal(asset, source, signal, price, vwap, prob):
    row = {
        "ativo": asset,
        "fonte": source,
        "sinal": signal,
        "preco": float(price),
        "vwap": float(vwap),
        "probabilidade": float(prob),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    try:
        supabase.table(TABLE).insert(row).execute()
        print(f"[{asset}] {signal} @ {price:.6f} vwap={vwap:.6f} prob={prob}%")
    except Exception as e:
        print("Erro ao salvar sinal:", e)

def process_round():
    for a in ASSETS:
        sym = a["symbol"]
        src = a["source"]
        try:
            if src == "binance":
                df = fetch_binance_klines_df(sym, interval="2m", limit=50)
                price = float(df["close"].iloc[-1])
                vwap = compute_vwap_from_df(df)
            elif src == "twelvedata" or src == "twelvedata_api":
                # twelve data expects "XAU/USD" or "EUR/USD"
                df = fetch_twelvedata_series(sym, interval="2min", outputsize=50)
                price = float(df["close"].iloc[-1])
                vwap = compute_vwap_from_df(df)
            else:
                print("Fonte desconhecida:", src)
                continue

            signal = decide_signal(price, vwap, threshold_pct=0.0015)
            prob = estimate_confidence(price, vwap) if signal != "NEUTRO" else 0.0

            # save always so dashboard shows last state
            save_signal(sym, src, signal, price, vwap, prob)

        except Exception as e:
            print(f"Erro processando {sym} ({src}): {e}")

def start_bot():
    print("🤖 Iniciando monitor VWAP (2m) — loop contínuo")
    while True:
        try:
            process_round()
        except Exception as e:
            print("Erro geral no round:", e)
        time.sleep(POLL_INTERVAL)

# if run directly
if __name__ == "__main__":
    start_bot()
