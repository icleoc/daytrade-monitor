# run_server.py
import threading
from monitor_vwap_real import start_all, app

if __name__ == "__main__":
    # inicia o bot em thread paralela
    t = threading.Thread(target=start_all, daemon=True)
    t.start()

    # roda o servidor Flask
    app.run(host="0.0.0.0", port=int(__import__('os').environ.get("PORT", 5000)))
