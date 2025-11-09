from monitor_vwap_real import app, start_bot
from threading import Thread

Thread(target=start_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
