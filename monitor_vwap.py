import os

print("=== TESTE DE VARIÁVEIS ===")
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
anon_key = os.getenv("SUPABASE_ANON_KEY")
print("SUPABASE_ANON_KEY:", anon_key[:8] + "..." if anon_key else "❌ NÃO ENCONTRADA")

if not os.getenv("SUPABASE_URL") or not anon_key:
    print("❌ Variáveis de ambiente não configuradas corretamente no Render.")
    print("➡️ Vá em Settings → Environment → Add Environment Variable e adicione:")
    print("SUPABASE_URL e SUPABASE_ANON_KEY")
else:
    print("✅ Variáveis detectadas com sucesso! Tudo certo.")
