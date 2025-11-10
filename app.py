from flask import Flask, render_template
from monitor.monitor_vwap_real import get_assets_data

app = Flask(__name__)

ASSETS = ['WINM23.SA', 'USDBRL=X', 'GC=F']  # exemplo mini-índice, dólar e ouro

@app.route('/')
def dashboard():
    data = get_assets_data(ASSETS, interval='15m', period='7d')
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
