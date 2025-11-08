import threading
import time
from flask import Flask
from monitor_vwap import main  # importa seu bot

# Cria servidor Flask para o Render detectar uma porta aberta
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot VWAP ativo e monitorando..."

def start_bot():
    # Executa o monitor em paralelo
    main()

if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=10000)
