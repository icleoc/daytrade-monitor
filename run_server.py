from flask import Flask
import threading
from monitor_vwap import start_bot, conectar_supabase

app = Flask(__name__)

@app.route('/')
def index():
    return "🚀 VWAP Bot ativo e monitorando!"

@app.route('/status')
def status():
    return {"status": "online", "supabase": conectar_supabase()}

def run_bot():
    start_bot()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
