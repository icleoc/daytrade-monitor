from flask import Flask, jsonify, render_template
from monitor_vwap_real import start_bot
from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
start_bot()  # Inicializa o monitor em background

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/signals")
def api_signals():
    result = supabase.table("ativos").select("*").execute()
    return jsonify(result.data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
