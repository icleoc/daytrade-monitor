from flask import Flask
from supabase import create_client, Client
import os
from monitor_vwap import main  # agora essa função existe!

app = Flask(__name__)

# Conexão Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)
print("✅ Conectado ao Supabase com sucesso!")

@app.route("/")
def index():
    return "🚀 Bot VWAP está rodando no Render!"

if __name__ == "__main__":
    main()  # inicia o bot
    app.run(host="0.0.0.0", port=10000)
