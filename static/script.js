async function fetchPrices() {
    const res = await fetch('/api/prices');
    const data = await res.json();
    for (let symbol in data.prices) {
        document.querySelector(`#card-${symbol} .price`).innerText = `$${data.prices[symbol].toFixed(2)}`;
        document.querySelector(`#card-${symbol} .vwap`).innerText = `VWAP: ${data.vwap[symbol].toFixed(2)}`;
    }
}

async function fetchHistorical(symbol) {
    const res = await fetch(`/api/historical/${symbol}`);
    return await res.json();
}

async function updateChart() {
    const dataBTC = await fetchHistorical('BTC');
    const ctx = document.getElementById('priceChart').getContext('2d');

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dataBTC.map(d => d.time),
            datasets: [{
                label: 'BTC/USD',
                data: dataBTC.map(d => d.price),
                borderColor: 'rgba(75,192,192,1)',
                fill: false
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

// Atualiza a cada minuto
fetchPrices();
updateChart();
setInterval(fetchPrices, 60000);
setInterval(updateChart, 60000);
