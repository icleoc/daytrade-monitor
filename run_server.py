# run_server.py
import os
import threading
from flask import Flask, render_template
from supabase import create_client
from datetime import datetime, timezone

# create supabase client (for dashboard quick queries)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE = os.getenv("SUPABASE_TABLE_SIGNALS", "sinais_vwap")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# import start_bot (delayed import to avoid running at import time if not desired)
from monitor_vwap_real import start_bot

app = Flask(__name__)
start_time = datetime.now(timezone.utc)

@app.route("/")
def dashboard():
    try:
        resp = supabase.table(TABLE).select("*").order("timestamp", desc=True).limit(50).execute()
        sinais = resp.data or []
    except Exception as e:
        print("Erro ao buscar sinais:", e)
        sinais = []
    return render_template("dashboard.html", sinais=sinais)

@app.route("/status")
def status():
    uptime_min = (datetime.now(timezone.utc) - start_time).total_seconds() / 60.0
    return {
        "status": "online",
        "uptime_min": round(uptime_min, 2),
        "assets": os.getenv("ASSETS")
    }

if __name__ == "__main__":
    # start monitor in background thread (daemon)
    t = threading.Thread(target=start_bot, daemon=True)
    t.start()
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
