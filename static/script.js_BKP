async function fetchData() {
    const res = await fetch("/api/data");
    return await res.json();
}

function gerarSinal(preco, vwap) {
    if (preco > vwap * 1.002) return "VENDA";
    if (preco < vwap * 0.998) return "COMPRA";
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
        const vwap_series = info.vwap_series;
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

        const times = candles.map(c => c.datetime);
        const open = candles.map(c => c.open);
        const high = candles.map(c => c.high);
        const low = candles.map(c => c.low);
        const close = candles.map(c => c.close);

        const traceCandles = {
            x: times,
            open, high, low, close,
            type: "candlestick",
            name: symbol,
            increasing: { line: { color: "#16a34a" } },
            decreasing: { line: { color: "#dc2626" } }
        };

        const traceVWAP = {
            x: times,
            y: vwap_series,
            mode: "lines",
            name: "VWAP",
            line: { color: "#3b82f6", width: 2 }
        };

        // Sinais no gráfico
        const sinais = times.map((t, i) => {
            const s = gerarSinal(close[i], vwap_series[i]);
            if (s === "HOLD") return null;
            return {
                x: [t],
                y: [close[i]],
                text: [s],
                mode: "text+markers",
                textposition: s === "COMPRA" ? "bottom center" : "top center",
                marker: { color: corSinal(s), size: 12 },
                textfont: { color: corSinal(s), size: 14 }
            };
        }).filter(Boolean);

        const layout = {
            title: `${symbol} — VWAP Dinâmico (15m)`,
            margin: { t: 50, b: 40 },
            xaxis: { showgrid: false },
            yaxis: { fixedrange: false }
        };

        const container = document.createElement("div");
        container.className = "chart";
        container.id = `chart-${symbol}`;
        charts.appendChild(container);

        Plotly.newPlot(container.id, [traceCandles, traceVWAP, ...sinais], layout, { responsive: true });
    });
}

setInterval(renderDashboard, 60000);
renderDashboard();
