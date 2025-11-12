async function loadData() {
    try {
        const res = await fetch('/api/data');
        const data = await res.json();

        data.forEach(asset => {
            const card = document.getElementById(asset.symbol);
            if (!card) return;

            card.querySelector('.price').textContent = asset.price;
            card.querySelector('.vwap').textContent = asset.vwap;

            const signalEl = card.querySelector('.signal');
            signalEl.textContent = asset.signal.toUpperCase();
            signalEl.style.color = asset.signal === 'buy' ? 'lime' :
                                   asset.signal === 'sell' ? 'red' : 'gray';

            // Plot do gráfico
            const chartData = asset.chart;
            const times = chartData.map(c => c.Datetime);
            const open = chartData.map(c => c.Open);
            const high = chartData.map(c => c.High);
            const low = chartData.map(c => c.Low);
            const close = chartData.map(c => c.Close);
            const vwap = chartData.map(c => c.vwap);

            const lastSignalIndex = chartData.length - 1;
            const signalMarker = {
                x: [times[lastSignalIndex]],
                y: [close[lastSignalIndex]],
                mode: "markers+text",
                text: asset.signal === "buy" ? "↑" : asset.signal === "sell" ? "↓" : "",
                textposition: "top center",
                textfont: { color: asset.signal === "buy" ? "lime" : "red", size: 20 },
                marker: { size: 0 }
            };

            const traceCandles = {
                x: times,
                open, high, low, close,
                type: "candlestick",
                name: asset.symbol,
            };

            const traceVWAP = {
                x: times,
                y: vwap,
                mode: "lines",
                line: { color: "orange", width: 1.5 },
                name: "VWAP"
            };

            const layout = {
                paper_bgcolor: "#1e1e1e",
                plot_bgcolor: "#1e1e1e",
                font: { color: "#fff" },
                margin: { t: 10, b: 20, l: 30, r: 10 },
                xaxis: { showgrid: false },
                yaxis: { showgrid: true, gridcolor: "#333" },
            };

            Plotly.newPlot(`chart-${asset.symbol}`, [traceCandles, traceVWAP, signalMarker], layout, {displayModeBar: false});
        });
    } catch (e) {
        console.error("Erro ao carregar dados:", e);
    }
}

loadData();
setInterval(loadData, 60000); // Atualiza a cada 1 minuto
