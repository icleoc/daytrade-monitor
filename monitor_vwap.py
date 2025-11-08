import os
import time
from supabase import create_client, Client
from datetime import datetime, timezone

# -----------------------------
# Configurações do Supabase
# -----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("❌ Configure SUPABASE_URL e SUPABASE_ANON_KEY nas variáveis de ambiente.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
print("✅ Conectado ao Supabase com sucesso!")

# -----------------------------
# Configurações do bot
# -----------------------------
ASSETS = os.getenv("ASSETS", "XAU/USD,BTC/USD,EUR/USD,IBOV").split(",")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))  # segundos

# -----------------------------
# Funções auxiliares
# -----------------------------
def buscar_ultimo_preco(asset):
    """Busca o último preço do ativo na tabela 'ativos'"""
    try:
        resp = supabase.table("ativos").select("*").eq("ativo", asset).order("timestamp", desc=True).limit(1).execute()
        if resp.data and len(resp.data) > 0:
            return float(resp.data[0]["preco"])
        return None
    except Exception as e:
        print(f"⚠️ Erro ao buscar preço de {asset}: {e}")
        return None

def calcular_sinal(asset, preco, vwap):
    """
    Estratégia simples:
    - Compra: preço abaixo da VWAP
    - Venda: preço acima da VWAP
    """
    if preco is None or vwap is None:
        return None
    if preco < vwap:
        return "COMPRA"
    elif preco > vwap:
        return "VENDA"
    else:
        return None

def gravar_alerta(asset, tipo_alerta, preco):
    """Grava alerta na tabela 'alerts'"""
    data = {
        "ativo": asset,
        "tipo_alerta": tipo_alerta,
        "preco": preco,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    try:
        supabase.table("alerts").insert(data).execute()
        print(f"💡 Alerta gerado: {asset} → {tipo_alerta} @ {preco}")
    except Exception as e:
        print(f"⚠️ Erro ao gravar alerta de {asset}: {e}")

# -----------------------------
# Função de monitoramento
# -----------------------------
def monitorar_sinais():
    for asset in ASSETS:
        preco = buscar_ultimo_preco(asset)
        if preco is None:
            print(f"⚠️ Sem preço disponível para {asset}")
            continue

        # Simulação de VWAP: média dos últimos 5 preços (pode ajustar)
        resp = supabase.table("ativos").select("*").eq("ativo", asset).order("timestamp", desc=True).limit(5).execute()
        precos = [float(p["preco"]) for p in resp.data] if resp.data else []
        vwap = sum(precos)/len(precos) if precos else preco

        sinal = calcular_sinal(asset, preco, vwap)
        if sinal:
            gravar_alerta(asset, sinal, preco)
        else:
            print(f"➡️ {asset}: Nenhum sinal gerado (preço = {preco}, VWAP = {vwap})")

# -----------------------------
# Loop principal
# -----------------------------
if __name__ == "__main__":
    print("🚀 Iniciando monitoramento de sinais contínuo...")
    while True:
        try:
            monitorar_sinais()
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"⚠️ Erro no loop principal: {e}")
            time.sleep(10)
