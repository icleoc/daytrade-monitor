from flask import Flask, render_template, jsonify
from monitor.monitor_vwap_real import get_all_data

app = Flask(__name__)

# Rota principal: renderiza o dashboard
@app.route('/')
def index():
    return render_template('dashboard.html')

# Rota API: retorna todos os dados em JSON
@app.route('/api/data')
def api_data():
    try:
        data = get_all_data()  # Função do monitor_vwap_real.py que retorna todos os ativos
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Roda o app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
