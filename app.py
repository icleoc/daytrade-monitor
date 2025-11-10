from flask import Flask, render_template, jsonify
from monitor_vwap_real import get_assets_data

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/data')
def api_data():
    assets_data = get_assets_data()
    return jsonify(assets_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
