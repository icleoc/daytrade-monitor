import os
import time
from datetime import datetime
from supabase import create_client, Client

# Conecta ao Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("❌ Configure SUPABASE_URL e SUPABASE_ANON_KEY nas variáveis de ambiente.")
    exit()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
print("✅ Conectado ao Supabase!")

# Função que insere dados no Supabase (simulação de sinal VWAP)
def registrar_sinal(ativo, preco, direcao):
    data = {
        "ativo": ativo,
        "preco": preco,
        "direcao": direcao,
        "timestamp": datetime.utcnow().isoformat(),
    }
    supabase.table("ativos").insert(data).execute()
    print(f"📊 Sinal registrado: {ativo} - {direcao} @ {preco}")

# Função principal (loop do bot)
def main():
    print("✅ Bot de monitoramento VWAP iniciado...")
    while True:
        try:
            # Simulação de leitura de preço (placeholder)
            ativo = "BTC/USD"
            preco = 70000.00  # Exemplo
            direcao = "compra"

            registrar_sinal(ativo, preco, direcao)

            print("⏳ Aguardando próximo ciclo...")
            time.sleep(60)  # 1 minuto entre execuções
        except Exception as e:
            print(f"❌ Erro no loop principal: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
