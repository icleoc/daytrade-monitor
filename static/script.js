async function fetchData() {
    const res = await fetch("/api/data");
    return await res.json();
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
        const candles = info.candles;
        const sinal = gerarSinal(price, vwap);
        const cor = corSinal(sinal);

        // CARD
        cards.innerHTML += `
            <div class="card" style="background:${cor}">
                <h2>${symbol}</h2>
                <p><strong>Preço:</strong> ${price.toFixed(2)}</p>
                <p><strong>VWAP:</strong> ${vwap.toFixed(2)}</p>
                <p class="sinal">${sinal}</p>
            </div>`;

        // Dados para gráfico real
        const times = candles.map(c => c.datetime);
        const open = candles.map(c => c.open);
        const high = candles.map(c => c.high);
        const low = candles.map(c => c.low);
        const close = candles.map(c => c.close);
        const vwapLine = Array(times.length).fill(vwap);

        const candlesPlot = {
            x: times,
            open: open,
            high: high,
            low: low,
            close: close,
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

        // Sinais sobre candles
        const sinais = candles.map((c, i) => {
            const s = gerarSinal(c.close, vwap);
            if (s === "HOLD") return null;
            return {
                x: [c.datetime],
                y: [c.close],
                text: [s],
                mode: "text+markers",
                textposition: s === "COMPRA" ? "bottom center" : "top center",
                marker: { color: corSinal(s), size: 12 },
                textfont: { color: corSinal(s), size: 14 }
            };
        }).filter(Boolean);

        const layout = {
            title: `${symbol} — VWAP Real (15m)`,
            margin: { t: 40, b: 30 },
            xaxis: { showgrid: false },
            yaxis: { fixedrange: false }
        };

        const container = document.createElement("div");
        container.className = "chart";
        container.id = `chart-${symbol}`;
        charts.appendChild(container);

        Plotly.newPlot(container.id, [candlesPlot, traceVWAP, ...sinais], layout, { responsive: true });
    });
}

setInterval(renderDashboard, 60000);
renderDashboard();
