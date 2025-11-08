import os
import time
import yfinance as yf
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Configurações Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("❌ Configure SUPABASE_URL e SUPABASE_ANON_KEY nas variáveis de ambiente.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
print("✅ Conectado ao Supabase com sucesso!")

# Ativos / tickers no Yahoo Finance
TICKERS = {
    "XAUUSD": "GC=F",       # Ouro futuro (confirme se funciona para você)
    "BTCUSD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "IBOV": "^BVSP"
}

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))  # segundos

def get_latest_price(ticker):
    """Retorna o preço de fechamento mais recente de ticker."""
    try:
        df = yf.download(tickers=ticker, period="1d", interval="1m", progress=False)
        if df is None or df.empty:
            return None
        latest = df["Close"].iloc[-1]
        return float(latest)
    except Exception as e:
        print(f"⚠️ Erro ao obter preço para {ticker}: {e}")
        return None

def gravar_preco(asset, price):
    data = {
        "ativo": asset,
        "preco": price,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        supabase.table("ativos").insert(data).execute()
        print(f"💾 Gravado {asset} = {price}")
    except Exception as e:
        print(f"⚠️ Erro ao gravar {asset}: {e}")

def monitorar():
    print(f"⏱️ Checando preços: {', '.join(TICKERS.keys())}")
    for asset, ticker in TICKERS.items():
        price = get_latest_price(ticker)
        if price is not None:
            gravar_preco(asset, price)
        else:
            print(f"⚠️ Sem preço válido para {asset}")

if __name__ == "__main__":
    print("🚀 Iniciando monitoramento em loop contínuo...")
    while True:
        try:
            monitorar()
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("🛑 Monitoramento interrompido pelo usuário.")
            break
        except Exception as e:
            print(f"⚠️ Erro no loop principal: {e}")
            time.sleep(10)
