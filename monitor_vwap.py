import os
import time
from datetime import datetime, timezone
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))
ASSETS = os.getenv("ASSETS", "BTC/USD,ETH/USD").split(",")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def conectar_supabase():
    """Verifica conexão com Supabase"""
    try:
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mensagem": "Teste de conexão OK"
        }
        supabase.table("logs").insert(data).execute()
        print("✅ Conectado ao Supabase!")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar Supabase: {e}")
        return False


def calcular_vwap(asset: str):
    """Função simulada (substitua com lógica real de VWAP)"""
    import random
    preco = random.uniform(100, 200)
    vwap = random.uniform(100, 200)
    sinal = "COMPRA" if preco < vwap else "VENDA"
    return {"ativo": asset, "preco": preco, "vwap": vwap, "sinal": sinal}


def enviar_sinal(sinal):
    """Envia sinal ao Supabase"""
    try:
        supabase.table("sinais").insert(sinal).execute()
        print(f"💾 Sinal inserido: {sinal}")
    except Exception as e:
        print(f"❌ Falha ao inserir sinal: {e}")


def main():
    """Executa uma rodada de cálculo VWAP"""
    print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} — Iniciando rodada de monitoramento...")
    for asset in ASSETS:
        sinal = calcular_vwap(asset.strip())
        enviar_sinal(sinal)
    print("✅ Rodada concluída.")


def start_bot():
    """Loop contínuo — usado pelo Flask (run_server.py)"""
    print("🤖 Iniciando loop contínuo do bot VWAP...")
    if not conectar_supabase():
        print("❌ Erro de conexão. Encerrando bot.")
        return

    while True:
        main()
        time.sleep(POLL_INTERVAL)
