from flask import Flask, render_template, jsonify
from helpers import get_all_data

app = Flask(__name__)

@app.route("/")
def dashboard():
    symbols = ["BTCUSD", "ETHUSD", "EURUSD", "XAUUSD"]
    return render_template("dashboard.html", symbols=symbols)

@app.route("/api/data")
def api_data():
    try:
        data = get_all_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
