const REFRESH_INTERVAL = 60000; // 60s

function createCard(symbol, lastPrice, signals, error) {
    const card = document.createElement("div");
    card.className = "card";

    let signalText = "HOLD";
    let cardColor = "#ccc";

    if (signals && signals.length > 0) {
        const lastSignal = signals[signals.length - 1].signal;
        signalText = lastSignal === "BUY" ? "COMPRA" : "VENDA";
        cardColor = lastSignal === "BUY" ? "#4CAF50" : "#F44336";
    }

    card.style.backgroundColor = cardColor;

    card.innerHTML = `
        <h2>${symbol}</h2>
        <p>${signalText}</p>
        <p>Último preço: ${lastPrice !== null ? lastPrice.toFixed(5) : "—"}</p>
        <p>${error ? `Erro: ${error}` : ""}</p>
    `;
    return card;
}

function createChart(symbol, df, signals) {
    const chartDiv = document.createElement("div");
    chartDiv.id = `chart-${symbol}`;
    chartDiv.className = "chart";

    if (!df || df.length === 0) {
        chartDiv.innerHTML = "Sem dados";
        return chartDiv;
    }

    const traceCandles = {
        x: df.map(d => d.datetime),
        open: df.map(d => d.open),
        high: df.map(d => d.high),
        low: df.map(d => d.low),
        close: df.map(d => d.close),
        type: 'candlestick',
        name: symbol
    };

    const traceVWAP = {
        x: df.map(d => d.datetime),
        y: df.map(d => d.vwap),
        type: 'scatter',
        mode: 'lines',
        line: { color: 'blue', width: 2 },
        name: 'VWAP'
    };

    const traceUpper = {
        x: df.map(d => d.datetime),
        y: df.map(d => d.upper_band),
        type: 'scatter',
        mode: 'lines',
        line: { color: 'rgba(0,0,255,0.3)', width: 1 },
        name: 'Upper Band'
    };

    const traceLower = {
        x: df.map(d => d.datetime),
        y: df.map(d => d.lower_band),
        type: 'scatter',
        mode: 'lines',
        line: { color: 'rgba(0,0,255,0.3)', width: 1 },
        name: 'Lower Band'
    };

    // Marcadores de sinais
    const buySignals = signals.filter(s => s.signal === "BUY");
    const sellSignals = signals.filter(s => s.signal === "SELL");

    const traceBuy = {
        x: buySignals.map(s => s.datetime),
        y: buySignals.map(s => s.price),
        mode: 'markers+text',
        text: buySignals.map(() => "COMPRA"),
        textposition: 'bottom center',
        marker: { color: 'green', size: 10, symbol: 'triangle-up' },
        name: 'BUY'
    };

    const traceSell = {
        x: sellSignals.map(s => s.datetime),
        y: sellSignals.map(s => s.price),
        mode: 'markers+text',
        text: sellSignals.map(() => "VENDA"),
        textposition: 'top center',
        marker: { color: 'red', size: 10, symbol: 'triangle-down' },
        name: 'SELL'
    };

    Plotly.newPlot(chartDiv, [traceCandles, traceVWAP, traceUpper, traceLower, traceBuy, traceSell], {
        title: symbol,
        xaxis: { rangeslider: { visible: false } },
        yaxis: { autorange: true }
    });

    return chartDiv;
}

async function updateDashboard() {
    try {
        const response = await fetch("/api/data");
        const data = await response.json();

        const cardsContainer = document.getElementById("cards");
        const chartsContainer = document.getElementById("charts");

        cardsContainer.innerHTML = "";
        chartsContainer.innerHTML = "";

        SYMBOLS.forEach(symbol => {
            const item = data[symbol];
            const card = createCard(symbol, item.last, item.signals, item.error);
            cardsContainer.appendChild(card);

            // Monta dados para gráfico
            if (item.signals && item.last !== null) {
                const df = item.df || [];
                const chartDiv = createChart(symbol, df, item.signals);
                chartsContainer.appendChild(chartDiv);
            }
        });
    } catch (e) {
        console.error("Erro ao atualizar dashboard:", e);
    }
}

updateDashboard();
setInterval(updateDashboard, REFRESH_INTERVAL);
