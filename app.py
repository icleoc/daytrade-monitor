from flask import Flask, jsonify, render_template
from monitor.monitor_vwap_real import get_all_vwap_data
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/vwap')
def vwap_data():
    data = get_all_vwap_data()
    return jsonify(data)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Monitor VWAP em execução."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
