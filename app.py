from flask import Flask, jsonify
import os

app = Flask(__name__)

# === ROTAS ===
@app.route("/vwap")
def vwap():
    return jsonify({"message": "VWAP route funcionando!"})

@app.route("/rsi")
def rsi():
    return jsonify({"message": "RSI route funcionando!"})

@app.route("/macd")
def macd():
    return jsonify({"message": "MACD route funcionando!"})

# Rota raiz para teste
@app.route("/")
def home():
    return jsonify({"message": "App rodando! Rotas disponíveis: /vwap, /rsi, /macd"})

# === DEBUG: mostra todas as rotas registradas ===
@app.before_first_request
def print_routes():
    print("=== Rotas registradas ===")
    for rule in app.url_map.iter_rules():
        print(rule)

# Porta obrigatória para Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"App iniciando na porta {port}")
    app.run(host="0.0.0.0", port=port)
