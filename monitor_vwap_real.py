#!/usr/bin/env python3
# monitor_vwap_real.py
# Monitor VWAP 2m em tempo real com Binance WebSocket + Supabase + Flask
# Preparado para deploy (Render). Leia comentários e ajuste variáveis de ambiente.

import os
import time
import json
import threading
import logging
import math
from collections import deque, defaultdict
from datetime import datetime, timezone
from typing import Dict, Any, Deque, Optional

import requests
from websocket import WebSocketApp
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Carregar .env localmente (Render usará env vars do serviço)
load_dotenv()

# Config e logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vwap_monitor")

# Variáveis de ambiente essenciais
SUPABASE_URL = os.environ.get("SUPABASE_URL")          # ex: https://xxxx.supabase.co
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")          # anon / service role depending on write needs
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
BINANCE_API_SECRET = os.environ.get("BINANCE_API_SECRET")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL e SUPABASE_KEY precisam estar definidas nas variáveis de ambiente.")
    # Não vamos encerrar para permitir desenvolvimento local; mas em produção configure.
if not BINANCE_API_KEY or not BINANCE_API_SECRET:
    logger.warning("BINANCE_API_KEY / BINANCE_API_SECRET não detectadas. Websockets públicos funcionarão, mas operações autenticadas (ordens) não.")


# Parâmetros do sistema
VWAP_WINDOW_MINUTES = 2        # timeframe VWAP (2 minutos)
KLINE_INTERVAL = "2m"          # solicitamos klines de 2m (Binance)
HYSTERESIS_PCT = float(os.environ.get("HYSTERESIS_PCT", "0.0008"))  # evita ruídos (0.08% default)
RECONNECT_DELAY = 5            # segundos antes de reconectar websocket
SUPABASE_TABLE = os.environ.get("SUPABASE_TABLE", "ativos")
SIGNAL_UPDATE_TABLE_COLUMN = "last_signal"  # coluna opcional para persistir sinal
PRICE_FIELD = "price"          # campo para armazenar price em supabase (se existir)

# Mapeamento simbólico (caso a tabela 'ativos' não contenha o símbolo exato da Binance)
DEFAULT_SYMBOL_MAP = {
    "BTCUSD": "btcusdt",
    "ETHUSD": "ethusdt",
    "XAUUSD": "xauusdt",   # pode não existir em Binance; preferível ter mapping na tabela 'ativos'
    "EURUSD": "eurusdt"
}

# Endpoints Binance stream (spot). Para futuros a URL muda — ajuste se necessário.
BINANCE_WS_BASE = "wss://stream.binance.com:9443/stream"

# Estruturas em memória para estado e cache
# Para cada símbolo: mantemos a barra corrente (incompleta) e a última barra 2m completa (para VWAP).
symbols_info: Dict[str, Dict[str, Any]] = {}
signals_cache: Dict[str, Dict[str, Any]] = {}
trade_buffers: Dict[str, Deque[Dict[str, Any]]] = defaultdict(lambda: deque(maxlen=10000))

# VWAP storage: para cada símbolo guardamos a soma_pv e soma_v da janela atual (2m)
vwap_state: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"sum_pv": 0.0, "sum_v": 0.0, "window_start": None})

# Thread control
ws_app: Optional[WebSocketApp] = None
ws_thread: Optional[threading.Thread] = None
stop_event = threading.Event()

# Flask app
app = Flask(__name__)


# ---------- Utilitários ----------
def now_ts() -> float:
    return time.time()


def to_millis(t: float) -> int:
    return int(t * 1000)


def safe_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def format_iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def fetch_assets_from_supabase() -> Dict[str, Dict[str, Any]]:
    """
    Carrega ativos da tabela Supabase 'ativos'.
    Espera que cada registro contenha:
      - id
      - name
      - symbol  (opcional; se ausente, usa DEFAULT_SYMBOL_MAP)
      - enabled (boolean) (opcional)
      - threshold (opcional)
    Retorna dict com chave=binance_symbol em lowercase -> registro
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("Supabase não configurado; não foi possível buscar ativos.")
        return {}

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?select=*"
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        out = {}
        for rec in data:
            raw_symbol = rec.get("symbol") or rec.get("ticker") or rec.get("asset") or rec.get("name")
            if raw_symbol:
                sym = raw_symbol.lower()
            else:
                # fallback: try mapping by uppercase name
                name = (rec.get("name") or "").upper()
                sym = DEFAULT_SYMBOL_MAP.get(name, None)
                if sym:
                    sym = sym.lower()
                else:
                    continue
            rec["binance_symbol"] = sym
            out[sym] = rec
        logger.info(f"Ativos carregados do Supabase: {list(out.keys())}")
        return out
    except Exception as e:
        logger.exception("Erro ao carregar ativos do Supabase: %s", e)
        return {}


def update_signal_in_supabase(binance_symbol: str, signal: str, price: float):
    """
    Atualiza coluna last_signal (e opcionalmente price) para o ativo no Supabase.
    Usa PATCH via REST para registro cujo binance_symbol corresponda.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.debug("Supabase não configurado; pulando persistência de sinal.")
        return

    # Tentamos localizar o registro por binance_symbol
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        # Primeiro obter id do registro com esse symbol
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?binance_symbol=eq.{binance_symbol}"
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        items = r.json()
        if not items:
            logger.debug("Nenhum registro Supabase com binance_symbol=%s", binance_symbol)
            return
        rec = items[0]
        rec_id = rec.get("id")
        if rec_id is None:
            # fallback: atualizar por binance_symbol com PATCH usando query
            patch_url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?binance_symbol=eq.{binance_symbol}"
        else:
            patch_url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?id=eq.{rec_id}"

        body = {SIGNAL_UPDATE_TABLE_COLUMN: signal}
        # opcional: atualizar preço
        if PRICE_FIELD:
            body[PRICE_FIELD] = price

        patch_headers = headers.copy()
        patch_headers["Prefer"] = "return=representation"
        r2 = requests.patch(patch_url, headers=patch_headers, json=body, timeout=8)
        r2.raise_for_status()
        logger.debug("Sinal atualizado no Supabase para %s -> %s", binance_symbol, signal)
    except Exception as e:
        logger.exception("Erro ao atualizar sinal no Supabase: %s", e)


# ---------- VWAP e lógica de sinal ----------
def compute_vwap_from_trades(trades: Deque[Dict[str, Any]]) -> Optional[float]:
    """
    Recebe deque de trades (cada item com price e qty e timestamp em ms).
    Computa VWAP sobre a janela atual (espera que trades contenham somente última janela).
    """
    sum_pv = 0.0
    sum_v = 0.0
    for t in trades:
        p = safe_float(t.get("price", 0.0))
        q = safe_float(t.get("qty", 0.0))
        sum_pv += p * q
        sum_v += q
    if sum_v == 0:
        return None
    return sum_pv / sum_v


def decide_signal(latest_price: float, vwap: float, prev_signal: Optional[str], hysteresis_pct: float = HYSTERESIS_PCT) -> str:
    """
    Regra simples de sinal:
      - Se price > vwap * (1 + h) => BUY
      - Se price < vwap * (1 - h) => SELL
      - Caso contrário, manter prev_signal (ou SELL por padrão)
    Histerese evita flicker.
    """
    if vwap is None:
        return prev_signal or "NEUTRAL"

    up_thresh = vwap * (1 + hysteresis_pct)
    down_thresh = vwap * (1 - hysteresis_pct)

    if latest_price > up_thresh:
        return "BUY"
    if latest_price < down_thresh:
        return "SELL"
    return prev_signal or "NEUTRAL"


# ---------- WebSocket listener e processamento ----------
def build_stream_url(symbols: Dict[str, Any]) -> str:
    """
    Monta URL de streams agregados da Binance: klines de 2m e trade para price.
    Ex: btcusdt@kline_2m/ethusdt@kline_2m/... e btcusdt@trade/...
    Limite de streams por conexão deve ser observado (1024 stream max)
    """
    streams = []
    for sym in symbols.keys():
        streams.append(f"{sym}@kline_{KLINE_INTERVAL}")
        streams.append(f"{sym}@trade")
    stream_query = "/".join(streams)
    return f"{BINANCE_WS_BASE}?streams={stream_query}"


def on_ws_message(ws, message):
    """
    Mensagens chegam no formato padrão: {"stream": "...", "data": { ... }}
    Tratamos 'kline' e 'trade'.
    """
    try:
        payload = json.loads(message)
    except Exception:
        logger.debug("Mensagem não JSON: %s", message)
        return

    data = payload.get("data", {})
    stream = payload.get("stream", "")

    # Kline events
    if "kline" in stream or data.get("e") == "kline":
        k = data.get("k") or data
        symbol = (k.get("s") or "").lower()
        is_closed = k.get("x", False)
        open_t = k.get("t")  # open time ms
        close_t = k.get("T") or k.get("t")  # close time ms (fallback)
        o = safe_float(k.get("o", 0))
        h = safe_float(k.get("h", 0))
        l = safe_float(k.get("l", 0))
        c = safe_float(k.get("c", 0))
        v = safe_float(k.get("v", 0))

        # typical price * volume
        tp = (h + l + c) / 3.0 if (h and l and c) else c
        pv = tp * v

        # atualize estado VWAP somente quando barra fechada (usar barra fechada garante precisão)
        if is_closed:
            # reset window state and compute VWAP for the just closed bar if necessário
            # Simples: para sinal usamos VWAP da última barra de 2m (padrão)
            vwap = None
            if v > 0:
                vwap = pv / v  # VWAP da barra (ponto de referência)
            # Armazenar no cache
            signals_cache[symbol] = signals_cache.get(symbol, {})
            signals_cache[symbol].update({
                "last_kline_close": c,
                "last_kline_vwap": vwap,
                "last_kline_ts": close_t,
                "last_kline_iso": datetime.fromtimestamp(close_t/1000, tz=timezone.utc).isoformat()
            })
            logger.debug("KLINE fechado %s @ %.8f VWAP(2m)=%.8f", symbol, c, vwap if vwap else float('nan'))
            # se tivermos preço atual, decidimos sinal usando vwap de barra fechada
            latest_price = signals_cache[symbol].get("latest_price", c)
            prev_signal = signals_cache[symbol].get("signal")
            new_signal = decide_signal(latest_price, vwap, prev_signal)
            if new_signal != prev_signal:
                signals_cache[symbol]["signal"] = new_signal
                signals_cache[symbol]["signal_ts"] = to_millis(time.time())
                logger.info("Sinal atualizado %s -> %s (price=%.6f vwap=%.6f)", symbol, new_signal, latest_price, vwap if vwap else float('nan'))
                # Persistir
                threading.Thread(target=update_signal_in_supabase, args=(symbol, new_signal, latest_price), daemon=True).start()

    # Trade events
    elif "trade" in stream or data.get("e") == "trade":
        symbol = (data.get("s") or "").lower()
        price = safe_float(data.get("p") or data.get("price") or 0)
        qty = safe_float(data.get("q") or data.get("qty") or 0)
        ts = int(data.get("T") or data.get("t") or to_millis(time.time()))
        # guardar trade em buffer (usado para cálculos intrabar)
        buf = trade_buffers[symbol]
        buf.append({"price": price, "qty": qty, "ts": ts})
        # atualizar latest price
        sc = signals_cache.get(symbol, {})
        sc["latest_price"] = price
        sc["latest_price_ts"] = ts
        signals_cache[symbol] = sc
        # opcional: calculo intrabar VWAP para mostrar no dashboard em tempo real
        # consideramos trades dentro dos últimos VWAP_WINDOW_MINUTES
        cutoff = to_millis(time.time()) - (VWAP_WINDOW_MINUTES * 60 * 1000)
        # remover trades antigos
        while buf and buf[0]["ts"] < cutoff:
            buf.popleft()
        intrabar_vwap = compute_vwap_from_trades(buf)
        if intrabar_vwap:
            sc["intrabar_vwap"] = intrabar_vwap
        # Decide sinal em tempo real usando intrabar_vwap se disponível
        prev_signal = sc.get("signal")
        new_signal = decide_signal(price, intrabar_vwap if intrabar_vwap is not None else sc.get("last_kline_vwap"), prev_signal)
        if new_signal != prev_signal:
            sc["signal"] = new_signal
            sc["signal_ts"] = to_millis(time.time())
            logger.info("Sinal realtime %s -> %s (price=%.6f intrabar_vwap=%s)", symbol, new_signal, price, f"{intrabar_vwap:.6f}" if intrabar_vwap else "n/a")
            threading.Thread(target=update_signal_in_supabase, args=(symbol, new_signal, price), daemon=True).start()
        signals_cache[symbol] = sc


def on_ws_error(ws, error):
    logger.exception("WS error: %s", error)


def on_ws_close(ws, close_status_code, close_msg):
    logger.warning("WS fechado: code=%s msg=%s", close_status_code, close_msg)


def on_ws_open(ws):
    logger.info("WS conectado com sucesso (Binance streams).")


def start_ws_stream(symbols_map: Dict[str, Any]):
    global ws_app
    # construir URL com streams para todos os símbolos em symbols_map
    if not symbols_map:
        logger.error("Nenhum símbolo para monitorar. Abortando websocket.")
        return

    url = build_stream_url(symbols_map)
    logger.info("Conectando ao Binance WS: %s", url)

    def _run():
        nonlocal url
        while not stop_event.is_set():
            try:
                ws = WebSocketApp(url,
                                  on_open=on_ws_open,
                                  on_message=on_ws_message,
                                  on_error=on_ws_error,
                                  on_close=on_ws_close)
                # armazenar global para permitir encerramento
                globals()['ws_app'] = ws
                ws.run_forever()
            except Exception as e:
                logger.exception("Exceção no loop do WS: %s", e)
            if stop_event.is_set():
                break
            logger.info("Reconectando websocket em %s segundos...", RECONNECT_DELAY)
            time.sleep(RECONNECT_DELAY)

    th = threading.Thread(target=_run, daemon=True, name="binance-ws")
    th.start()
    return th


# ---------- Flask API Endpoints ----------
@app.route("/api/signals", methods=["GET"])
def api_signals():
    """
    Retorna JSON com sinais atuais para o dashboard.
    Formato:
    {
      "symbol": {
         "signal": "BUY"/"SELL"/"NEUTRAL",
         "latest_price": 123.45,
         "intrabar_vwap": 123.4,
         "last_kline_vwap": 123.5,
         "last_kline_iso": "...",
         "color": "green"/"red"/"gray"
      },
      ...
    }
    """
    response = {}
    for sym, sc in signals_cache.items():
        sig = sc.get("signal", "NEUTRAL")
        color = "gray"
        if sig == "BUY":
            color = "green"
        elif sig == "SELL":
            color = "red"
        response[sym] = {
            "signal": sig,
            "color": color,
            "latest_price": sc.get("latest_price"),
            "intrabar_vwap": sc.get("intrabar_vwap"),
            "last_kline_vwap": sc.get("last_kline_vwap"),
            "last_kline_iso": sc.get("last_kline_iso"),
            "signal_ts": sc.get("signal_ts"),
        }
    return jsonify(response)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "time": format_iso(time.time()),
        "watched_symbols": list(signals_cache.keys()),
    })


# ---------- Inicialização e reload de ativos ----------
def refresh_assets_and_restart_ws():
    """
    Recupera ativos do Supabase, popula symbols_info e (re)inicia websocket.
    Chamada no bootstrap e pode ser chamada periodicamente/por webhook.
    """
    global symbols_info, ws_thread, stop_event
    logger.info("Atualizando ativos do Supabase...")
    assets = fetch_assets_from_supabase()
    if not assets:
        logger.warning("Nenhum ativo retornado do Supabase; manter o que já existe.")
        return

    # Filtrar ativos habilitados (se coluna enabled existir)
    filtered = {}
    for sym, rec in assets.items():
        enabled = rec.get("enabled", True)
        if enabled:
            filtered[sym] = rec

    # Atualizar estado
    symbols_info = filtered

    # iniciar/reiniciar websocket
    # sinaliza parada para thread antiga
    if ws_thread and ws_thread.is_alive():
        logger.info("Parando websocket antigo...")
        try:
            stop_event.set()
            # fechar conexão se disponível
            if globals().get('ws_app'):
                try:
                    globals()['ws_app'].close()
                except Exception:
                    pass
            ws_thread.join(timeout=3)
        except Exception:
            pass
        stop_event.clear()

    logger.info("Iniciando websocket para símbolos: %s", list(symbols_info.keys()))
    ws_thread_local = start_ws_stream(symbols_info)
    globals()['ws_thread'] = ws_thread_local


def periodic_asset_refresher(interval_sec: int = 300):
    """
    Atualiza ativos periodicamente (ex.: para refletir alterações feitas no Supabase dashboard).
    """
    while True:
        try:
            refresh_assets_and_restart_ws()
        except Exception:
            logger.exception("Erro no refresher de ativos.")
        time.sleep(interval_sec)


# ---------- Entrypoint ----------
def start_background_services():
    # Carregar ativos uma vez e iniciar websocket
    refresh_assets_and_restart_ws()

    # Iniciar thread que periodicamente sincroniza a tabela de ativos (caso admin altere)
    refresher = threading.Thread(target=periodic_asset_refresher, kwargs={"interval_sec": 300}, daemon=True, name="asset-refresher")
    refresher.start()
    logger.info("Serviços de background iniciados.")


if __name__ == "__main__":
    # Iniciar serviços background e Flask (modo produção: Render usa gunicorn; este arquivo pode ser apontado como entrypoint)
    start_background_services()
    port = int(os.environ.get("PORT", 5000))
    # O debug deve ficar off em produção
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
