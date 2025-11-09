from flask import Flask, jsonify, render_template
import random
import time

app = Flask(__name__)

# === Configuração de ativos monitorados ===
ATIVOS = ["PETR4", "VALE3", "ITUB4", "BBDC4", "MGLU3", "BBAS3"]

def gerar_dados_ativo(ativo):
    """Simula dados de indicadores para cada ativo"""
    vwap = round(random.uniform(9.5, 11.5), 4)
    rsi = round(random.uniform(25, 80), 2)
    macd = round(random.uniform(-1.5, 1.5), 3)

    # Geração de sinal baseado em regras simples
    if rsi < 30 and macd > 0:
        sinal = "COMPRA"
    elif rsi > 70 and macd < 0:
        sinal = "VENDA"
    else:
        sinal = "NEUTRO"

    return {
        "ativo": ativo,
        "vwap": vwap,
        "rsi": rsi,
        "macd": macd,
        "sinal": sinal,
        "hora": time.strftime("%H:%M:%S")
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dados')
def dados():
    """Retorna dados atualizados de todos os ativos"""
    dados = [gerar_dados_ativo(ativo) for ativo in ATIVOS]
    return jsonify(dados)

@app.route('/vwap')
def vwap_route():
    return jsonify({"vwap": round(random.uniform(9.5, 11.5), 4)})

@app.route('/rsi')
def rsi_route():
    return jsonify({"rsi": round(random.uniform(25, 80), 2)})

@app.route('/macd')
def macd_route():
    return jsonify({"macd": round(random.uniform(-1.5, 1.5), 3)})

@app.route('/status')
def status():
    return jsonify({"status": "API do Monitor VWAP funcionando!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
