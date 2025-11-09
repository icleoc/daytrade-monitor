# run_server.py
import os
from flask import Flask, render_template
from supabase import create_client, Client
from datetime import datetime, timezone

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE = os.getenv("SUPABASE_TABLE_SIGNALS", "sinais_vwap")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def dashboard():
    try:
        resp = supabase.table(TABLE).select("*").order("timestamp", desc=True).limit(50).execute()
        sinais = resp.data or []
    except Exception as e:
        print("Erro ao buscar sinais:", e)
        sinais = []
    return render_template("dashboard.html", sinais=sinais)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
