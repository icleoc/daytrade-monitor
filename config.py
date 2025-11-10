import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (caso esteja rodando localmente)
load_dotenv()

# ==============================
# 🔐 CHAVES E CREDENCIAIS
# ==============================
# Estas variáveis devem estar definidas no painel do Render (Environment)
CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "")

# ==============================
# ⚙️ CONFIGURAÇÕES DE API
# ==============================
CRYPTOCOMPARE_BASE = "https://min-api.cryptocompare.com/data/v2"

# ==============================
# 💹 PARÂMETROS DE ANÁLISE VWAP
# ==============================
SYMBOLS = ["BTCUSDT", "ETHUSDT"]      # Pares monitorados
TIMEFRAME_MINUTES = 5                 # Intervalo das velas
CANDLE_LIMIT = 100                    # Quantidade de candles analisados
BAND_STD_MULTIPLIER = 2               # Multiplicador do desvio padrão nas bandas
UPDATE_INTERVAL_SECONDS = 60          # Tempo entre atualizações (em segundos)

# ==============================
# 🌐 CONFIGURAÇÕES DO SERVIDOR FLASK
# ==============================
FLASK_HOST = "0.0.0.0"
FLASK_PORT = int(os.getenv("PORT", 5000))
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# ==============================
# 🧠 CONFIGURAÇÕES AVANÇADAS
# ==============================
# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Arquivo de logs (opcional)
LOG_FILE = os.path.join(BASE_DIR, "logs", "app.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
