# monitor_vwap_real.py
import os
import time
import logging
from datetime import datetime, timezone

import requests
import pandas as pd
from flask import Flask, render_template, jsonify
from supabase import create_client, Client

# -------------------- Config & Logging --------------------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vwap_coinbase")

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL e SUPABASE_KEY precisam estar definidas nas Environment Variables.")
supabase: Client = create_client(SUPABASE_URL or "", SUPABASE_KEY or "")

# Monitor settings
# Coinbase product symbols (use esses exatos)
ASSETS = os.environ.get("ASSETS", "BTC-USD,ETH-USD,XAU-USD,EUR-USD").split(",")
# Granularidade de candles em segundos (120s = 2min)
COINBASE_GRANULARITY = int(os.environ.get("COINBASE_GRANULARITY", "120"))
# Quantidade de candles para cálculo VWAP (ex.: 5 candles de 2m = janela de 10m) — ajuste se quiser
VWAP_CANDLES = int(os.environ.get("VWAP_CANDLES", "5"))
# Intervalo entre atualizações do loop (em segundos). Deve ser >= COINBASE_GRANULARITY.
REFRESH_INTERVAL = int(os.environ.get("REFRESH_INTERVAL", str(COINBASE_GRANULARITY)))

# Flask app
app = Flask(__name__)

# -------------------- Utilitários --------------------
def now_iso():
    return datetime.now(timezone.utc).isoformat()

def fetch_coinbase_candles(symbol: str, granularity: int, limit: int = 300):
    """
    Busca candles da Coinbase Exchange public REST API.
    Retorna DataFrame com colunas: time, low, high, open, close, volume
    Coinbase returns list of [time, low, high, open, close, volume] (unix seconds)
    """
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity={granularity}"
    # Coinbase permite limitar via params? usamos a resposta padrão.
    try:
        res = requests.get(url, timeout=12)
        res.raise_for_status()
        data = res.json()
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Resposta Coinbase vazia ou inválida")
        df = pd.DataFrame(data, columns=["time", "low", "high", "open", "close", "volume"])
        # convert types
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df[["low","high","open","close","volume"]] = df[["low","high","open","close","volume"]].astype(float)
        df.sort_values("time", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except Exception as e:
        logger.warning("Falha ao buscar candles Coinbase %s: %s", symbol, e)
        return pd.DataFrame(columns=["time","low","high","open","close","volume"])

def compute_vwap_from_df(df: pd.DataFrame, candles: int):
    """
    Calcula VWAP usando os últimos `candles` da df.
    """
    if df.empty:
        return None
    tail = df.tail(candles)
    # typical price * volume
    tp = (tail["high"] + tail["low"] + tail["close"]) / 3.0
    tpv = tp * tail["volume"]
    vol_sum = tail["volume"].sum()
    if vol_sum == 0:
        return None
    return float(tpv.sum() / vol_sum)

def upsert_ativo(nome: str, preco: float, vwap: float, sinal: str):
    """
    Insere ou atualiza registro na tabela public.ativos
    Estrutura esperada da tabela (ver schema_ativos.sql abaixo)
    """
    try:
        payload = {
            "nome": nome,
            "preco": round(float(preco), 6) if preco is not None else None,
            "vwap": round(float(vwap), 6) if vwap is not None else None,
            "sinal": sinal,
            "atualizado_em": now_iso()
        }
        supabase.table("ativos").upsert(payload).execute()
        logger.debug("Upsert na tabela ativos: %s -> %s", nome, sinal)
    except Exception as e:
        logger.exception("Erro ao upsertar no Supabase para %s: %s", nome, e)

# -------------------- Loop principal --------------------
def start_all():
    """
    Inicia loop contínuo que:
    - busca candles da Coinbase por asset
    - calcula VWAP (janela configurável)
    - decide sinal (BUY/SELL/NEUTRAL)
    - persiste no Supabase
    """
    logger.info("Iniciando VWAP Monitor (Coinbase). Assets: %s", ASSETS)
    # segurança: se REFRESH_INTERVAL < granularity, forçamos igual
    if REFRESH_INTERVAL < COINBASE_GRANULARITY:
        logger.warning("REFRESH_INTERVAL < COINBASE_GRANULARITY -> definindo REFRESH_INTERVAL = COINBASE_GRANULARITY")
        # não alteramos a env var, apenas usamos o valor correto localmente
        sleep_time = COINBASE_GRANULARITY
    else:
        sleep_time = REFRESH_INTERVAL

    while True:
        for symbol in ASSETS:
            try:
                df = fetch_coinbase_candles(symbol, COINBASE_GRANULARITY)
                vwap = compute_vwap_from_df(df, VWAP_CANDLES)
                last_close = float(df["close"].iat[-1]) if (not df.empty and len(df) > 0) else None

                # decidir sinal com histerese mínima: se price > vwap => BUY, < vwap => SELL, else NEUTRAL
                if last_close is None or vwap is None:
                    signal = "NEUTRAL"
                else:
                    if last_close > vwap:
                        signal = "BUY"
                    elif last_close < vwap:
                        signal = "SELL"
                    else:
                        signal = "NEUTRAL"

                # persistir
                upsert_ativo(symbol, last_close if last_close is not None else 0.0, vwap if vwap is not None else 0.0, signal)
                logger.info("%s -> sinal=%s preco=%s vwap=%s", symbol, signal, last_close, vwap)
            except Exception as e:
                logger.exception("Erro processando %s: %s", symbol, e)
        # dormir antes do próximo ciclo
        time.sleep(sleep_time)

# -------------------- Endpoints Flask --------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/signals")
def api_signals():
    try:
        resp = supabase.table("ativos").select("*").execute()
        data = resp.data or []
        return jsonify(data)
    except Exception as e:
        logger.exception("Erro ao buscar sinais do Supabase: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "time": now_iso(),
        "assets_monitored": ASSETS
    })

# -------------------- Entrypoint --------------------
# Nota: run_server.py iniciará start_all() em thread; gunicorn usará app.
if __name__ == "__main__":
    # se executado diretamente para debug local
    t = None
    try:
        t = __import__("threading").Thread(target=start_all, daemon=True)
        t.start()
    except Exception:
        logger.exception("Erro ao iniciar thread de background.")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
