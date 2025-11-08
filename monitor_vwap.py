from supabase import create_client, Client
from datetime import datetime
import random
import os

# Conexão com Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Configure SUPABASE_URL e SUPABASE_KEY nas variáveis de ambiente.")
else:
    print("✅ Conectado ao Supabase com sucesso!")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ativos monitorados
ASSETS = ["BTC/USDT", "ETH/USDT", "XAU/USD", "EUR/USD"]

def gerar_sinais():
    """Gera sinais de compra ou venda simulados."""
    sinais = []
    for ativo in ASSETS:
        tipo = random.choice(["compra", "venda", "neutro"])
        if tipo == "compra":
            mensagem = "🟢 COMPRA AGORA — preço abaixo do VWAP"
        elif tipo == "venda":
            mensagem = "🔴 VENDA AGORA — preço acima do VWAP"
        else:
            mensagem = "⚪ AGUARDE — sem sinal definido"

        sinais.append({
            "ativo": ativo,
            "tipo": tipo,
            "mensagem": mensagem,
            "timestamp": datetime.utcnow().isoformat()  # UTC — convertido no front-end
        })
    return sinais
