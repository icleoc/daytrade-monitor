import os
import logging
from flask import Flask, render_template, jsonify
from helpers import get_all_assets_data

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    try:
        data = get_all_assets_data()
        return jsonify(data)
    except Exception as e:
        logging.exception("Erro ao coletar dados")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
