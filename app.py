from flask import Flask, jsonify, render_template
from threading import Thread, Event
import os
import time
from monitor_vwap_real import MonitorVWAP


app = Flask(__name__, static_folder='static', template_folder='templates')


# Instancia o monitor (usa variáveis de ambiente)
monitor = MonitorVWAP()
stop_event = Event()


@app.route('/')
def index():
return render_template('dashboard.html')


@app.route('/api/signals')
def api_signals():
return jsonify(monitor.get_signals())


@app.route('/vwap')
def vwap_test():
# rota de teste simples
return jsonify({"vwap": monitor.get_sample_vwap()})




def background_loop(stop_event):
# roda o monitor em loop
while not stop_event.is_set():
try:
monitor.poll_once()
except Exception as e:
app.logger.exception('Erro no poll_once: %s', e)
interval = int(os.getenv('POLL_INTERVAL', '15'))
stop_event.wait(interval)




if __name__ == '__main__':
# start background thread
t = Thread(target=background_loop, args=(stop_event,), daemon=True)
t.start()
port = int(os.getenv('PORT', '5000'))
app.run(host='0.0.0.0', port=port)
