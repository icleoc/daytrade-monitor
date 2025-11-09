from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/vwap")
def vwap():
    return jsonify({"message": "VWAP endpoint funcionando!"})

@app.route("/rsi")
def rsi():
    return jsonify({"message": "RSI endpoint funcionando!"})

@app.route("/macd")
def macd():
    return jsonify({"message": "MACD endpoint funcionando!"})

if __name__ == "__main__":
    # O Render exige host 0.0.0.0 e porta da variável de ambiente PORT
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
