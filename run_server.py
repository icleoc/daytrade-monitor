from flask import Flask, jsonify, render_template
from monitor_vwap_real import start_background_thread, supabase

app = Flask(__name__)

# Inicia o monitor em background
start_background_thread()

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/signals')
def api_signals():
    from monitor_vwap_real import get_signals
    return jsonify(get_signals())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
