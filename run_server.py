from flask import Flask, jsonify
import threading
import time
import os
from supabase import create_client, Client
from monitor_vwap import start_bot  # mantém o bot rodando em background

# 🔹 Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
start_time = time.time()

# 🔹 Roda o bot VWAP em background
def run_bot():
    print("⚙️ Iniciando bot VWAP em background...")
    start_bot()

threading.Thread(target=run_bot, daemon=True).start()
print("✅ Bot de monitoramento VWAP iniciado...")

# 🔹 Endpoint de status
@app.route('/status')
def status():
    uptime = round((time.time() - start_time) / 60, 2)
    return jsonify({
        "status": "online",
        "uptime_minutos": uptime,
        "mensagem": "🚀 Bot VWAP está ativo no Render"
    })

# 🔹 Endpoint de sinais
@app.route('/sinais')
def sinais():
    try:
        data = supabase.table("sinais_vwap").select("*").order("timestamp", desc=True).limit(10).execute()
        return jsonify(data.data)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# 🔹 Endpoint raiz
@app.route('/')
def home():
    return "🚀 Bot VWAP está online e operando no Render!"

# 🔹 Inicia o servidor Flask
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor Flask rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)

def start_bot():
    print("🤖 Executando monitor VWAP uma vez (loop já está no main).")
    main()
    try:
        while True:
            # Aqui você chama a função principal de monitoramento
            main()
            time.sleep(int(os.getenv("POLL_INTERVAL", 60)))  # intervalo de checagem
    except KeyboardInterrupt:
        print("🛑 Bot encerrado manualmente.")

