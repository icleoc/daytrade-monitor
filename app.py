from flask import Flask, jsonify, render_template, send_from_directory, request
from monitor.monitor_vwap_real import get_all_vwap_data, get_chart_data_for_ticker
import os


app = Flask(__name__, template_folder='templates', static_folder='static')


# Dashboard
@app.route('/')
def index():
return render_template('dashboard.html')


# JSON API - vwap summary for all assets
@app.route('/api/vwap')
def api_vwap():
data = get_all_vwap_data()
return jsonify(data)


# API: chart data for a ticker
@app.route('/api/chart/<ticker>')
def api_chart(ticker):
period = request.args.get('period', '1d')
interval = request.args.get('interval', '15m')
chart = get_chart_data_for_ticker(ticker, period=period, interval=interval)
return jsonify(chart)


# Serve static files explicitly if needed
@app.route('/static/<path:filename>')
def static_files(filename):
return send_from_directory('static', filename)


if __name__ == '__main__':
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
