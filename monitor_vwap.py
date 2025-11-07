#!/usr/bin/env python3
"""
VWAP Monitor - Leo Edition
--------------------------
Monitora XAUUSD, BTCUSD, EURUSD e IBOV
Detecta cruzamento do preço com VWAP + filtro EMA21 + volume
Envia alertas para o Supabase (tabela 'alerts')
"""

import os
import time
import json
from datetime import datetime
import pandas as pd
import yfinance as yf
import requests
import ta

# ======== CONFIGURAÇÕES ========
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_TABLE = "alerts"
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))  # segundos

WATCHLIST = {
    "XAUUSD": "GC=F",      # Ouro (Futuros)
    "BTCUSD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "IBOV": "^BVSP"
}

EMA_PERIOD = 21
VOLUME_SMA_PERIOD = 20
MIN_VOLUME_MULTIPLIER = 1.0
MIN_PROB_BASE = 0.65


# ======== FUNÇÕES AUXILIARES ========
def fetch_ohlcv(ticker, period="2d", interval="1m", lookback=500):
    df = yf.download(tickers=ticker, period=period, interval=interval, progress=False)
    if df is None or df.empty:
        return None
    return df.tail(lookback)


def compute_vwap(df):
    df = df.copy()
    df["typ"] = (df["High"] + df["Low"] + df["Close"]) / 3
    df["pv"] = df["typ"] * df["Volume"]
    df["date"] = df.index.date
    vwap_list = []
    for d, group in df.groupby("date"):
        cum_pv = group["pv"].cumsum()
        cum_vol = group["Volume"].cumsum()
        v = (cum_pv / cum_vol).values
        vwap_list.extend(v)
    df["VWAP"] = vwap_list
    return df


def compute_indicators(df):
    df["EMA21"] = df["Close"].ewm(span=EMA_PERIOD, adjust=False).mean()
    df["VOL_SMA20"] = df["Volume"].rolling(VOLUME_SMA_PERIOD).mean()
    return df


def detect_signal(df):
    if df is None or len(df) < VOLUME_SMA_PERIOD + 5:
        return None
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if (prev["Close"] <= prev["VWAP"]) and (last["Close"] > last["VWAP"]):
        direction = "BUY"
    elif (prev["Close"] >= prev["VWAP"]) and (last["Close"] < last["VWAP"]):
        direction = "SELL"
    else:
        return None

    # Filtro EMA
    if direction == "BUY" and last["Close"] < last["EMA21"]:
        return None
    if direction == "SELL" and last["Close"] > last["EMA21"]:
        return None

    # Filtro Volume
    vol_ok = False
    if last["Volume"] and last["VOL_SMA20"]:
        if last["Volume"] >= last["VOL_SMA20"] * MIN_VOLUME_MULTIPLIER:
            vol_ok = True

    prob = MIN_PROB_BASE + (0.1 if vol_ok else 0)
    body = abs(last["Close"] - last["Open"])
    rng = max(last["High"] - last["Low"], 1e-6)
    if body / rng > 0.6:
        prob += 0.05
    prob = min(0.99, prob)

    return {
        "time": last.name.isoformat(),
        "direction": direction,
        "price": float(last["Close"]),
        "vwap": float(last["VWAP"]),
        "volume": float(last["Volume"]),
        "ema21": float(last["EMA21"]),
        "prob": round(prob, 2)
    }


def send_to_supabase(payload):
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        if r.status_code in (201, 204):
            print(f"[{datetime.now()}] Alerta enviado: {payload}")
        else:
            print(f"[{datetime.now()}] Erro {r.status_code}: {r.text}")
    except Exception as e:
        print("Erro ao enviar Supabase:", e)


def main_loop():
    print("🚀 Iniciando monitor VWAP...")
    while True:
        for sym_name, ticker in WATCHLIST.items():
            try:
                df = fetch_ohlcv(ticker)
                if df is None or df.empty:
                    print(f"{sym_name}: sem dados.")
                    continue
                df = compute_vwap(df)
                df = compute_indicators(df)
                sig = detect_signal(df)
                if sig:
                    payload = {
                        "symbol": sym_name,
                        "action": sig["direction"],
                        "price": sig["price"],
                        "volume": sig["volume"],
                        "timestamp": sig["time"],
                        "source": "python-monitor",
                        "meta": {
                            "vwap": sig["vwap"],
                            "ema21": sig["ema21"],
                            "prob": sig["prob"]
                        }
                    }
                    send_to_supabase(payload)
                time.sleep(0.5)
            except Exception as e:
                print("Erro loop:", e)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ Configure SUPABASE_URL e SUPABASE_ANON_KEY nas variáveis de ambiente.")
        exit(1)
    main_loop()
