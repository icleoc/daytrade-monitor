from flask import Flask, jsonify, render_template
import threading
from monitor_vwap_real import start_bot
from supabase import create_client
import os

# ----------------------------
# Configurações Supabase
# ----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------
# Flask App
# ----------------------------
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/signals")
def api_signals():
    try:
        res = supabase.table("ativos").select("*").execute()
        data = res.data
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

# ----------------------------
# Rodando o bot em thread separada
# ----------------------------
threading.Thread(target=start_bot, daemon=True).start()

# ----------------------------
# Run Flask
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
