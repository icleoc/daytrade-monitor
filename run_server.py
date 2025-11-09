from flask import Flask, jsonify
from monitor_vwap_real import start_background_thread, supabase

app = Flask(__name__)

# Inicia o monitor em background
start_background_thread()

@app.route("/api/signals", methods=["GET"])
def get_signals():
    try:
        response = supabase.table("ativos").select("*").execute()
        if response.data:
            return jsonify(response.data)
        else:
            return jsonify([]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "<h2>VWAP Monitor está rodando!</h2><p>Acesse /api/signals para ver os sinais.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
