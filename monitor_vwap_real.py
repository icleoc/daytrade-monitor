#!/usr/bin/env python3
# monitor_vwap_real.py - versão final com dashboard HTML e Supabase integração completa

import os
import time
import json
import threading
import logging
from collections import deque, defaultdict
from datetime import datetime, timezone

import requests
from websocket import WebSocketApp
from flask import Flask, jsonify, render_template_string
from dotenv import load_dotenv

load_dotenv()

# ---------------------- CONFIGURAÇÕES ----------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vwap")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_TABLE = os.environ.get("SUPABASE_TABLE", "ativos")

VWAP_WINDOW_MINUTES = 2
HYSTERESIS_PCT = 0.0008
BINANCE_WS_BASE = "wss://stream.binance.com:9443/stream"

DEFAULT_SYMBOLS = ["btcusdt", "ethusdt", "eurusdt"]
KLINE_INTERVAL = "2m"

# ---------------------- VARIÁVEIS ----------------------

signals_cache = {}
trade_buffers = defaultdict(lambda: deque(maxlen=10000))
stop_event = threading.Event()
ws_thread = None
ws_app = None

app = Flask(__name__)

# ---------------------- FUNÇÕES SUPABASE ----------------------

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def fetch_assets():
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("⚠️ Supabase não configurado, usando símbolos padrão.")
        return DEFAULT_SYMBOLS
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?select=*", headers=supabase_headers(), timeout=10)
        r.raise_for_status()
        data = r.json()
        syms = [d.get("symbol", "").lower() for d in data if d.get("enabled", True)]
        return [s for s in syms if s]
    except Exception as e:
        logger.exception("Erro ao buscar ativos: %s", e)
        return DEFAULT_SYMBOLS

def update_signal(symbol, signal, price):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return
    try:
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?symbol=eq.{symbol}"
        body = {"last_signal": signal, "price": price, "updated_at": datetime.utcnow().isoformat()}
        requests.patch(url, headers={**supabase_headers(), "Prefer": "return=minimal"}, json=body, timeout=6)
    except Exception as e:
        logger.error("Erro ao atualizar Supabase %s: %s", symbol, e)

# ---------------------- VWAP E SINAIS ----------------------

def safe_float(x): 
    try: return float(x)
    except: return 0.0

def compute_vwap(trades):
    sum_pv = sum(safe_float(t["price"]) * safe_float(t["qty"]) for t in trades)
    sum_v = sum(safe_float(t["qty"]) for t in trades)
    return sum_pv / sum_v if sum_v else None

def decide_signal(price, vwap, prev_signal):
    if vwap is None: return prev_signal or "NEUTRAL"
    up = vwap * (1 + HYSTERESIS_PCT)
    down = vwap * (1 - HYSTERESIS_PCT)
    if price > up: return "BUY"
    if price < down: return "SELL"
    return prev_signal or "NEUTRAL"

# ---------------------- WEBSOCKET ----------------------

def build_url(symbols):
    streams = []
    for s in symbols:
        streams.append(f"{s}@kline_{KLINE_INTERVAL}")
        streams.append(f"{s}@trade")
    return f"{BINANCE_WS_BASE}?streams={'/'.join(streams)}"

def on_message(ws, msg):
    data = json.loads(msg)
    stream = data.get("stream", "")
    d = data.get("data", {})

    # TRADE
    if "trade" in stream:
        s = d["s"].lower()
        p = safe_float(d["p"])
        q = safe_float(d["q"])
        ts = d["T"]
        buf = trade_buffers[s]
        buf.append({"price": p, "qty": q, "ts": ts})
        cutoff = time.time() * 1000 - VWAP_WINDOW_MINUTES * 60 * 1000
        while buf and buf[0]["ts"] < cutoff:
            buf.popleft()
        vwap = compute_vwap(buf)
        prev = signals_cache.get(s, {}).get("signal")
        new = decide_signal(p, vwap, prev)
        signals_cache[s] = {
            "symbol": s,
            "price": p,
            "vwap": vwap,
            "signal": new,
            "updated": datetime.utcnow().isoformat()
        }
        if new != prev:
            threading.Thread(target=update_signal, args=(s, new, p), daemon=True).start()
            logger.info("→ %s %s | P=%.2f VWAP=%.2f", s, new, p, vwap or 0)

def start_ws(symbols):
    global ws_thread, ws_app
    url = build_url(symbols)
    logger.info("Conectando WS Binance: %s", url)

    def run():
        while not stop_event.is_set():
            try:
                ws = WebSocketApp(url, on_message=on_message)
                globals()["ws_app"] = ws
                ws.run_forever()
            except Exception as e:
                logger.error("Erro WS: %s", e)
            time.sleep(5)

    ws_thread = threading.Thread(target=run, daemon=True)
    ws_thread.start()

# ---------------------- FLASK ENDPOINTS ----------------------

@app.route("/")
def dashboard():
    html = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>VWAP Monitor</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; background:#0f111a; color:white; text-align:center; margin:0; padding:0; }
            h1 { background:#111; padding:15px; margin:0; font-weight:400; }
            #cards { display:flex; flex-wrap:wrap; justify-content:center; padding:20px; gap:20px; }
            .card { width:200px; padding:15px; border-radius:15px; color:white; box-shadow:0 0 10px #000; transition:transform 0.2s; }
            .card:hover { transform:scale(1.05); }
            .green { background:#16a34a; }
            .red { background:#dc2626; }
            .gray { background:#4b5563; }
            .price { font-size:1.4em; font-weight:bold; }
            .signal { font-size:1.1em; margin-top:5px; }
            small { color:#9ca3af; }
        </style>
        <script>
            async function loadData(){
                const r = await fetch('/api/signals');
                const data = await r.json();
                const cards = document.getElementById('cards');
                cards.innerHTML = '';
                for (const [sym, info] of Object.entries(data)){
                    const div = document.createElement('div');
                    div.className = 'card ' + info.color;
                    div.innerHTML = `
                        <h3>${sym.toUpperCase()}</h3>
                        <div class="price">$${info.latest_price?.toFixed(2) || '-'}</div>
                        <div class="signal">${info.signal}</div>
                        <small>VWAP: ${info.vwap ? info.vwap.toFixed(2) : '-'}</small><br>
                        <small>Atualizado: ${new Date(info.signal_ts || Date.now()).toLocaleTimeString()}</small>
                    `;
                    cards.appendChild(div);
                }
            }
            setInterval(loadData, 30000);
            window.onload = loadData;
        </script>
    </head>
    <body>
        <h1>VWAP Monitor em Tempo Real</h1>
        <div id="cards"></div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/api/signals")
def api_signals():
    out = {}
    for s, v in signals_cache.items():
        sig = v.get("signal", "NEUTRAL")
        color = "gray" if sig == "NEUTRAL" else ("green" if sig == "BUY" else "red")
        out[s] = {
            "signal": sig,
            "color": color,
            "latest_price": v.get("price"),
            "vwap": v.get("vwap"),
            "signal_ts": v.get("updated")
        }
    return jsonify(out)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "symbols": list(signals_cache.keys()), "updated": datetime.utcnow().isoformat()})

# ---------------------- MAIN ----------------------

def start_all():
    symbols = fetch_assets()
    start_ws(symbols)
    logger.info("Ativos monitorados: %s", symbols)

if __name__ == "__main__":
    start_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
