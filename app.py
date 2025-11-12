from flask import Flask, jsonify, render_template, request
import helpers

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/data")
def api_data():
    try:
        symbol = request.args.get("symbol", "BTCUSDT")
        timeframe = request.args.get("timeframe", "1h")  # default
        data_obj = helpers.get_symbol_data(symbol, timeframe)
        return jsonify({"symbol": symbol, "timeframe": timeframe, "data": data_obj})
    except Exception as e:
        app.logger.error(f"Erro ao buscar dados: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
