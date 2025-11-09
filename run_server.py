# run_server.py
from flask import Flask, render_template
from monitor_vwap_real import supabase  # reuse client if available
import os

app = Flask(__name__)

TABLE = os.getenv("SUPABASE_TABLE_SIGNALS", "sinais_vwap")

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
