from flask import Flask, render_template
from supabase import create_client, Client
import os

app = Flask(__name__)

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def dashboard():
    try:
        # Busca os últimos 50 sinais da tabela 'ativos'
        response = supabase.table("ativos").select("*").order("timestamp", desc=True).limit(50).execute()
        data = response.data
    except Exception as e:
        data = []
        print("Erro ao carregar dados:", e)

    return render_template("dashboard.html", sinais=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
