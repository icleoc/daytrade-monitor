from flask import Flask, render_template_string
from monitor_vwap_real import start_background_thread

app = Flask(__name__)
start_background_thread()

# HTML do dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>VWAP Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }
        h1 { text-align: center; }
        .cards { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 20px; }
        .card {
            background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            width: 200px; text-align: center; font-size: 16px;
        }
        .card h2 { margin: 0 0 10px 0; font-size: 18px; }
        .signal-COMPRA { color: green; font-weight: bold; }
        .signal-VENDA { color: red; font-weight: bold; }
        .signal-NEUTRO { color: gray; font-weight: bold; }
    </style>
</head>
<body>
    <h1>VWAP Monitor</h1>
    <div class="cards" id="cards"></div>

    <script>
        async function fetchSignals() {
            try {
                const res = await fetch('/api/signals');
                const data = await res.json();
                const cardsContainer = document.getElementById('cards');
                cardsContainer.innerHTML = '';
                for (const [asset, info] of Object.entries(data)) {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.innerHTML = `
                        <h2>${asset}</h2>
                        <p>Preço: ${info.preco !== null ? info.preco : '-'}</p>
                        <p>VWAP: ${info.vwap !== null ? info.vwap.toFixed(2) : '-'}</p>
                        <p class="signal-${info.sinal}">Sinal: ${info.sinal}</p>
                    `;
                    cardsContainer.appendChild(card);
                }
            } catch (e) {
                console.error("Erro ao buscar sinais:", e);
            }
        }

        // Atualiza a cada 10 segundos
        fetchSignals();
        setInterval(fetchSignals, 10000);
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
