// ============================
// CONFIG
// ============================
const API_URL = "/api/vwap";  
const REFRESH = 60 * 1000; // 60s

// ============================
// CRIA CARDS DINAMICAMENTE
// ============================
const container = document.getElementById("cards");
const template = document.getElementById("card-template");

function createCards() {
    container.innerHTML = ""; // limpa tudo
    SYMBOLS.forEach(sym => {
        const card = template.content.cloneNode(true);
        card.querySelector(".sym").textContent = sym;
        container.appendChild(card);
    });
}

// ============================
// ATUALIZA DADOS E GRÁFICOS
// ============================
async function updateData() {
    try {
        const res = await fetch(API_URL);
        const json = await res.json();

        if (!json.assets) return;

        json.assets.forEach(asset => {
            const card = [...document.querySelectorAll(".card")]
                .find(c => c.querySelector(".sym").textContent === asset.symbol);

            if (!card) return;

            // status
            card.querySelector(".status").textContent = asset.signal || "—";
            card.querySelector(".price").textContent =
                `Último preço: ${asset.last_price}`;

            // gráfico
            const chartDiv = card.querySelector(".chart");

            Plotly.react(chartDiv, [
                {
                    x: asset.timestamps,
                    y: asset.prices,
                    name: "Preço",
                    mode: "lines"
                },
                {
                    x: asset.timestamps,
                    y: asset.vwap,
                    name: "VWAP",
                    mode: "lines"
                }
            ], {
                margin: { t: 20, l: 40, r: 20, b: 30 },
                height: 360
            });
        });

    } catch (err) {
        console.error("Erro ao atualizar dashboard:", err);
    }
}

// ============================
// START
// ============================
createCards();
updateData();
setInterval(updateData, REFRESH);
