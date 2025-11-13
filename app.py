from flask import Flask, render_template, jsonify
import os
from helpers import get_all_data
import config


app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
def dashboard():
# PASSAGEM DOS SÍMBOLOS PARA O TEMPLATE
return render_template('dashboard.html', symbols=config.SYMBOLS, update_interval=config.UPDATE_INTERVAL_SECONDS)


@app.route('/api/data')
def api_data():
try:
data = get_all_data()
return jsonify(data)
except Exception as e:
return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
