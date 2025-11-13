document.addEventListener("DOMContentLoaded", async () => {
    const symbols = ["BTCUSDT", "ETHUSDT", "EURUSD", "XAUUSD"];

    async function fetchData() {
        const response = await fetch("/api/data");
        return await response.json();
    }

    function updateCard(symbol, data) {
        const card = document.querySelector(`#${symbol}`);
        if (!card) return;

        const priceEl = card.querySelector(".price");
        const signalEl = card.querySelector(".signal");

        if (priceEl) priceEl.textContent = data.price ? `$${data.price}` : "N/A";
        if (signalEl) signalEl.textContent = data.signal || "NEUTRAL";

        // Atualiza cor do card conforme o sinal
        card.classList.remove("buy", "sell", "neutral");
        if (data.signal === "BUY") card.classList.add("buy");
        else if (data.signal === "SELL") card.classList.add("sell");
        else card.classList.add("neutral");
    }

    function renderChart(symbol, data) {
        const container = document.getElementById(`${symbol}-chart`);
        if (!container) return;

        container.innerHTML = ""; // limpa o gráfico anterior

        const chart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 250,
            layout: { background: { color: "#fafafa" }, textColor: "#000" },
            grid: { vertLines: { color: "#eee" }, horzLines: { color: "#eee" } },
        });

        const candleSeries = chart.addCandlestickSeries();
        const vwapSeries = chart.addLineSeries({ color: "#007bff", lineWidth: 2 });
        const upperBandSeries = chart.addLineSeries({ color: "#28a745", lineWidth: 1, lineStyle: 1 });
        const lowerBandSeries = chart.addLineSeries({ color: "#dc3545", lineWidth: 1, lineStyle: 1 });

        if (data.candles && data.vwap) {
            candleSeries.setData(data.candles);
            vwapSeries.setData(data.vwap);
            upperBandSeries.setData(data.upper_band);
            lowerBandSeries.setData(data.lower_band);
        }
    }

    async function update() {
        const result = await fetchData();

        symbols.forEach(symbol => {
            const data = result[symbol];
            if (!data) return;
            updateCard(symbol, data);
            renderChart(symbol, data);
        });
    }

    await update();
    setInterval(update, 60000);
});
