from flask import Flask, render_template, jsonify
from monitor_vwap_real import start_background_thread, supabase

app = Flask(__name__)

start_background_thread()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/signals")
def api_signals():
    data = supabase.table("ativos").select("*").execute().data
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
