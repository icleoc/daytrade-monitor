from flask import Flask, render_template
from monitor_vwap import gerar_sinais

app = Flask(__name__)

@app.route('/')
def dashboard():
    sinais = gerar_sinais()
    return render_template("dashboard.html", sinais=sinais)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
