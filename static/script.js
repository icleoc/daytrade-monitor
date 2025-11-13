async function fetchData() {
    const response = await fetch("/api/data");
    const data = await response.json();
    return data;
}

function gerarSinal(price, vwap) {
    if (price > vwap * 1.002) return "VENDA";
    if (price < vwap * 0.998) return "COMPRA";
    return "HOLD";
}

function corSinal(sinal) {
    if (sinal === "COMPRA") return "#16a34a";
    if (sinal === "VENDA") return "#dc2626";
    return "#6b7280";
}

async function renderDashboard() {
    const data = await fetchData();
    const cards = document.getElementById("cards-container");
    const charts = document.getElementById("charts-container");
    cards.innerHTML = "";
    charts.innerHTML = "";

    SYMBOLS.forEach(symbol => {
        const info = data[symbol];
        if (!info || info.error) {
            cards.innerHTML += `<div class="card error">${symbol}<br>Erro: ${info?.error || "Sem dados"}</div>`;
            return;
        }

        const price = info.price;
        const vwap = info.vwap;
        const sinal = gerarSinal(price, vwap);
        const cor = corSinal(sinal);

        // Card
        cards.innerHTML += `
            <div class="card" style="background:${cor}">
                <h2>${symbol}</h2>
                <p><strong>Preço:</strong> ${price.toFixed(2)}</p>
                <p><strong>VWAP:</strong> ${vwap.toFixed(2)}</p>
                <p class="sinal">${sinal}</p>
            </div>`;

        // Gráfico simulado com candles e VWAP
        const times = Array.from({ length: 20 }, (_, i) => `T${i}`);
        const prices = times.map((_, i) => vwap * (1 + (Math.random() - 0.5) / 50));
        const vwapLine = Array(times.length).fill(vwap);

        const candles = {
            x: times,
            open: prices.map(p => p * (1 - 0.001)),
            high: prices.map(p => p * (1 + 0.002)),
            low: prices.map(p => p * (1 - 0.002)),
            close: prices,
            type: "candlestick",
            name: symbol
        };

        const traceVWAP = {
            x: times,
            y: vwapLine,
            mode: "lines",
            name: "VWAP",
            line: { color: "#3b82f6", width: 2 }
        };

        const sinais = prices.map((p, i) => {
            const s = gerarSinal(p, vwap);
            if (s === "HOLD") return null;
            return {
                x: times[i],
                y: p,
                text: s,
                mode: "text+markers",
                textposition: s === "COMPRA" ? "bottom center" : "top center",
                marker: { color: corSinal(s), size: 12 },
                textfont: { color: corSinal(s), size: 14 }
            };
        }).filter(Boolean);

        const layout = {
            title: `${symbol} — VWAP`,
            margin: { t: 40, b: 30 },
            xaxis: { showgrid: false },
            yaxis: { fixedrange: false }
        };

        const container = document.createElement("div");
        container.className = "chart";
        container.id = `chart-${symbol}`;
        charts.appendChild(container);

        Plotly.newPlot(container.id, [candles, traceVWAP, ...sinais], layout, { responsive: true });
    });
}

setInterval(renderDashboard, 60000); // 1x/min
renderDashboard();
