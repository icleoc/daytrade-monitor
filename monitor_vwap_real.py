# monitor_vwap_real.py
import os
import time
import requests
import pandas as pd
from datetime import datetime, timezone
from supabase import create_client, Client
from binance_client import fetch_binance_klines_df

# -------------------------
# Config e clientes
# -------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TWELVE_KEY = os.getenv("TWELVE_API_KEY")
ASSETS_RAW = os.getenv("ASSETS", "BTCUSDT:binance,ETHUSDT:binance,XAU/USD:twelvedata,EUR/USD:twelvedata")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "120"))  # 2 minutos
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

# -------------------------
# Twelve Data helper
# -------------------------
def fetch_twelvedata_series(symbol: str, interval: str = "2min", outputsize: int = 100, retry=3):
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
    attempt = 0
    backoff = 1.5
    while attempt < retry:
        try:
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            j = r.json()
            if "values" not in j:
                raise RuntimeError(f"TwelveData retornou sem 'values': {j}")
            vals = j["values"]
            df = pd.DataFrame(vals)
            # Ensure numeric
            for col in ("open","high","low","close"):
                df[col] = pd.to_numeric(df[col], errors="coerce")
            if "volume" in df.columns:
                df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0.0)
            else:
                df["volume"] = 0.0
            # reverse to chronological
            df = df[::-1].reset_index(drop=True)
            # convert datetime if present
            if "datetime" in df.columns:
                df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
            return df
        except Exception as e:
            attempt += 1
            wait = backoff ** attempt
            print(f"TwelveData error (attempt {attempt}/{retry}): {e}; sleeping {wait}s")
            time.sleep(wait)
    raise RuntimeError("Falha ao obter dados TwelveData após retries.")

# -------------------------
# VWAP & decision logic
# -------------------------
def compute_vwap_from_df(df: pd.DataFrame):
    # expects columns high, low, close, volume
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    vol = df["volume"] if "volume" in df.columns else pd.Series([0]*len(df))
    if vol.sum() > 0:
        vwap = (tp * vol).sum() / vol.sum()
        return float(vwap)
    else:
        # fallback -> SMA of typical price
        return float(tp.mean())

def decide_signal(price: float, vwap: float, threshold_pct=0.0015):
    # hysteresis zone to avoid noise (default 0.15%)
    if price < vwap * (1 - threshold_pct):
        return "COMPRA"
    elif price > vwap * (1 + threshold_pct):
        return "VENDA"
    else:
        return "NEUTRO"

def estimate_confidence(price: float, vwap: float):
    diff = abs(price - vwap) / vwap
    prob = min(round(diff * 100 * 8, 2), 99.0)  # heuristic scaling
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
    except Exception as e:
        print("Erro ao salvar sinal no Supabase:", e)

# -------------------------
# Single round processor
# -------------------------
def process_round():
    for a in ASSETS:
        sym = a["symbol"]
        src = a["source"]
        try:
            if src == "binance":
                df = fetch_binance_klines_df(sym, interval="2m", limit=50)
                price = float(df["close"].iloc[-1])
                vwap = compute_vwap_from_df(df)
            elif src.startswith("twelvedata"):
                df = fetch_twelvedata_series(sym, interval="2min", outputsize=50)
                price = float(df["close"].iloc[-1])
                vwap = compute_vwap_from_df(df)
            else:
                print("Fonte desconhecida:", src)
                continue

            signal = decide_signal(price, vwap, threshold_pct=0.0015)
            prob = estimate_confidence(price, vwap) if signal != "NEUTRO" else 0.0

            save_signal(sym, src, signal, price, vwap, prob)
            print(f"[{sym}] {signal} price={price:.6f} vwap={vwap:.6f} prob={prob}%")
        except Exception as e:
            print(f"Erro processando {sym} ({src}): {e}")

# -------------------------
# Runner / start_bot (used by run_server.py)
# -------------------------
def start_bot():
    print("🤖 Iniciando monitor VWAP real (2m) — loop contínuo")
    # initial warm-up
    while True:
        try:
            process_round()
        except Exception as e:
            print("Erro geral no round:", e)
        # wait POLL_INTERVAL seconds (should be 120)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    start_bot()
