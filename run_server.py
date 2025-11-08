from flask import Flask
from supabase import create_client, Client
import os
import threading
import time
from monitor_vwap import main  # importa o bot

app = Flask(__name__)

# Conecta ao Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)
print("✅ Conectado ao Supabase com sucesso!")

@app.route("/")
def index():
    return "🚀 Bot VWAP está online e operando no Render!"

# Função que roda o bot em thread separada (para não travar o Flask)
def start_bot():
    print("⚙️ Iniciando bot VWAP em background...")
    try:
        main()
    except Exception as e:
        print(f"❌ Erro ao rodar o bot: {e}")

if __name__ == "__main__":
    # Inicia o bot em paralelo
    thread = threading.Thread(target=start_bot)
    thread.start()

    # Inicia o Flask (Render exige uma porta aberta)
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor Flask rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)
