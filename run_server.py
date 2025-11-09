# run_server.py
import threading
from monitor_vwap_real import start_all, app

if __name__ == "__main__":
    # inicia o bot em thread paralela (daemon)
    t = threading.Thread(target=start_all, daemon=True)
    t.start()

    # inicia Flask (Gunicorn usará este app quando executar Procfile)
    app.run(host="0.0.0.0", port=int(__import__('os').environ.get("PORT", 5000)))
