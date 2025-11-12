async function loadData() {
    try {
        const res = await fetch("/api/data");
        const data = await res.json();

        const container = document.getElementById("dashboard");
        container.innerHTML = "";

        for (const [symbol, candles] of Object.entries(data)) {
            if (!candles || candles.length === 0) continue;

            const card = document.createElement("div");
            card.className = "card";

            const title = document.createElement("h2");
            title.textContent = symbol;
            card.appendChild(title);

            const canvas = document.createElement("canvas");
            card.appendChild(canvas);

            container.appendChild(card);

            const labels = candles.map(c => c.timestamp);
            const closes = candles.map(c => c.close);
            const opens = candles.map(c => c.open);

            // Último candle = ponto de entrada (plotando sinal)
            const lastIndex = closes.length - 1;
            const signalData = new Array(closes.length).fill(null);
            signalData[lastIndex] = closes[lastIndex];

            new Chart(canvas, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Fechamento",
                            data: closes,
                            borderColor: "#f00",
                            borderWidth: 2,
                            tension: 0.3
                        },
                        {
                            label: "Sinal Entrada",
                            data: signalData,
                            borderColor: "#0f0",
                            pointRadius: 8,
                            showLine: false
                        }
                    ]
                },
                options: {
                    plugins: { legend: { display: true } },
                    scales: {
                        x: { display: false },
                        y: { display: true }
                    }
                }
            });
        }
    } catch (err) {
        console.error("Erro ao carregar dados:", err);
    }
}

loadData();
setInterval(loadData, 60000);
