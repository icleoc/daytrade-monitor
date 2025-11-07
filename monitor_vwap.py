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



print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
anon_key = os.getenv("SUPABASE_ANON_KEY")
print("SUPABASE_ANON_KEY:", anon_key[:8] + "..." if anon_key else "❌ NÃO ENCONTRADA")

if not os.getenv("SUPABASE_URL") or not anon_key:
    print("❌ Variáveis de ambiente não configuradas corretamente no Render.")
    print("➡️ Vá em Settings → Environment → Add Environment Variable e adicione:")
    print("SUPABASE_URL e SUPABASE_ANON_KEY")
else:
    print("✅ Variáveis detectadas com sucesso! Tudo certo.")

