import os
from flask import Flask, render_template, jsonify
from helpers import fetch_all_symbols
import config

app = Flask(__name__)

@app.route('/')
def home():
    return render_template(
        'dashboard.html',
        symbols=config.SYMBOLS,
        update_interval=config.UPDATE_INTERVAL_SECONDS
    )

@app.route('/api/data')
def api_data():
    data = fetch_all_symbols()
    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
