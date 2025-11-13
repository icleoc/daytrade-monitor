from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import logging
import os


load_dotenv()


import config
from helpers import get_all_assets_data


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.route('/')
def index():
return render_template('dashboard.html', symbols=config.SYMBOLS, update_interval=config.UPDATE_INTERVAL_SECONDS)


@app.route('/api/data')
def api_data():
data = get_all_assets_data(config.SYMBOLS)
return jsonify(data)


if __name__ == '__main__':
app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=config.DEBUG)
