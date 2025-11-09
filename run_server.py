# run_server.py
from monitor_vwap_real import app, start_bot
from threading import Thread

# Inicia o bot em background
Thread(target=start_bot, daemon=True).start()

# Executa o Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
