import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Configure SUPABASE_URL e SUPABASE_ANON_KEY nas variáveis de ambiente.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("✅ Conectado ao Supabase!")
data = {"ativo": "TESTE", "preco": 1234.56}
supabase.table("ativos").insert(data).execute()
print("💾 Teste de inserção enviado com sucesso.")
