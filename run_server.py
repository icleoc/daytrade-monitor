from flask import Flask, render_template_string, jsonify
from monitor_vwap_real import start_background_thread, current_signals
import os

app = Flask(__name__)
start_background_thread()

# Template HTML do dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>VWAP Monitor</title>
<style>
body { font-family: Arial; background: #f4f4f4; padding: 20px; }
.cards { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }
.card { background: #fff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); width: 200px; text-align: center; }
.signal-COMPRA { color: green; font-weight: bold; }
.signal-VENDA { color: red; font-weight: bold; }
.signal-NEUTRO { color: gray; font-weight: bold; }
</style>
</head>
<body>
<h1>VWAP Monitor</h1>
<div class="cards" id="cards">Carregando...</div>
<script>
const refreshInterval = {{ refresh_interval | default(10) }} * 1000;
async function fetchSignals() {
    try {
        const res = await fetch('/api/signals');
        const data = await res.json();
        const container = document.getElementById('cards');
        container.innerHTML = '';
        for (const [asset, info] of Object.entries(data)) {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h2>${asset}</h2>
                <p>Preço: ${info.preco !== null ? info.preco : '-'}</p>
                <p>VWAP: ${info.vwap !== null ? info.vwap.toFixed(2) : '-'}</p>
                <p class="signal-${info.sinal}">Sinal: ${info.sinal}</p>`;
            container.appendChild(card);
        }
    } catch (e) {
        console.error("Erro:", e);
    }
}
fetchSignals();
setInterval(fetchSignals, refreshInterval);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    refresh_interval = int(os.environ.get("REFRESH_INTERVAL", 10))
    return render_template_string(HTML_TEMPLATE, refresh_interval=refresh_interval)

@app.route("/api/signals")
def api_signals():
    return jsonify(current_signals)

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
