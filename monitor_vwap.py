import os
import time
from supabase import create_client, Client
from datetime import datetime
import random  # usado para simular preço; substitua pela API real depois

# -----------------------------
# Configurações do Supabase
# -----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("❌ Configure SUPABASE_URL e SUPABASE_ANON_KEY nas variáveis de ambiente.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# -----------------------------
# Ativos e intervalo
# -----------------------------
ASSETS = os.getenv("ASSETS", "XAU/USD,BTC/USD,EUR/USD,IBOV").split(",")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))

# -----------------------------
# Função para simular VWAP (substituir por cálculo real depois)
# -----------------------------
def get_vwap_simulado(asset):
    # Simula um preço aleatório
    return round(random.uniform(100, 200), 2)

# -----------------------------
# Função para gravar no Supabase
# -----------------------------
def gravar_vwap(asset, price):
    data = {
        "ativo": asset,
        "preco": price,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        supabase.table("ativos").insert(data).execute()
        print(f"💾 VWAP de {asset} gravado: {price}")
    except Exception as e:
        print(f"⚠️ Erro ao gravar {asset}: {e}")

# -----------------------------
# Função principal de monitoramento
# -----------------------------
def monitorar_vwap():
    print(f"⏱️ Checando VWAPs dos ativos: {', '.join(ASSETS)}")
    for asset in ASSETS:
        price = get_vwap_simulado(asset)
        gravar_vwap(asset, price)

# -----------------------------
# Loop principal
# -----------------------------
if __name__ == "__main__":
    print("✅ Conectado ao Supabase!")
    print(f"🚀 Iniciando monitoramento em loop infinito a cada {POLL_INTERVAL} segundos...")
    
    while True:
        try:
            monitorar_vwap()
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"⚠️ Erro no loop principal: {e}")
            time.sleep(10)
