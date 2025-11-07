import os
import time
from supabase import create_client, Client

import os
print("DEBUG VARIÁVEIS:")
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_ANON_KEY:", os.getenv("SUPABASE_ANON_KEY")[:10], "...")


# Função para colorir os logs no terminal
def log(msg, tipo="info"):
    cores = {
        "info": "\033[94m",   # azul
        "ok": "\033[92m",     # verde
        "erro": "\033[91m",   # vermelho
        "aviso": "\033[93m",  # amarelo
    }
    reset = "\033[0m"
    print(f"{cores.get(tipo, '')}{msg}{reset}")

# 1️⃣ Lendo variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# 2️⃣ Checando se as variáveis estão configuradas
if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    log("❌ Configure SUPABASE_URL e SUPABASE_ANON_KEY nas variáveis de ambiente.", "erro")
    log("⚙️ No Render: vá em Settings → Environment → Add Environment Variable", "aviso")
    exit(1)

# 3️⃣ Conectando ao Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    log("✅ Conectado ao Supabase com sucesso!", "ok")
except Exception as e:
    log(f"❌ Erro ao conectar ao Supabase: {e}", "erro")
    exit(1)

# 4️⃣ Teste de inserção (para confirmar escrita)
try:
    data = {
        "ativo": "XAU/USD",
        "preco": 2674.5,
        "sentimento": "teste",
        "probabilidade": 0.75,
    }
    response = supabase.table("ativos").insert(data).execute()
    log(f"💾 Inserção de teste bem-sucedida: {response.data}", "ok")
except Exception as e:
    log(f"❌ Erro ao inserir dados: {e}", "erro")
    exit(1)

# 5️⃣ Loop simulado (para monitoramento futuro)
log("🔁 Iniciando loop de monitoramento (simulação)...", "info")

while True:
    # Aqui futuramente virá a análise real-time (ex: dados TradingView, Binance, etc)
    log("📊 Monitorando ativos... (teste ativo)", "info")
    time.sleep(30)
