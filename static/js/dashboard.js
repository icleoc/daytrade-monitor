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
            const signal = new Array(closes.length).fill(null);
            signal[closes.length - 1] = closes[closes.length - 1];

            new Chart(canvas, {
                type: 'line',
                data: {
                    labels,
                    datasets: [
                        {
                            label: "Preço Fechamento",
                            data: closes,
                            borderColor: "#ff4747",
                            borderWidth: 2,
                            tension: 0.3
                        },
                        {
                            label: "Sinal de Entrada",
                            data: signal,
                            borderColor: "#00ff00",
                            pointRadius: 7,
                            pointBackgroundColor: "#00ff00",
                            showLine: false
                        }
                    ]
                },
                options: {
                    plugins: { legend: { labels: { color: "#fff" } } },
                    scales: {
                        x: { display: false },
                        y: { ticks: { color: "#fff" } }
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
