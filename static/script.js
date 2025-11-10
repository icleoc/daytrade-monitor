const dashboard = document.getElementById('dashboard');
const updateInterval = 15000; // 15s

async function fetchData() {
    const res = await fetch('/api/data');
    const data = await res.json();
    return data;
}

function createCard(asset) {
    const card = document.createElement('div');
    card.className = 'card';
    card.id = `card-${asset.ticker}`;

    const title = document.createElement('h2');
    title.textContent = asset.ticker;
    card.appendChild(title);

    const price = document.createElement('p');
    price.textContent = `Preço: ${asset.price ?? 'Sem dados'}`;
    card.appendChild(price);

    const vwap = document.createElement('p');
    vwap.textContent = `VWAP: ${asset.vwap ?? 'Sem dados'}`;
    card.appendChild(vwap);

    const signal = document.createElement('p');
    signal.textContent = asset.signal ? `⚖️ ${asset.signal}` : 'Sem dados';
    card.appendChild(signal);

    const chartCanvas = document.createElement('canvas');
    chartCanvas.id = `chart-${asset.ticker}`;
    chartCanvas.height = 200;
    card.appendChild(chartCanvas);

    const updated = document.createElement('p');
    updated.id = `updated-${asset.ticker}`;
    updated.textContent = `Atualizado em: ${new Date().toLocaleTimeString()}`;
    card.appendChild(updated);

    dashboard.appendChild(card);
    return chartCanvas;
}

function updateCard(asset) {
    const card = document.getElementById(`card-${asset.ticker}`);
    if (!card) return;

    card.style.backgroundColor = asset.signal === 'Compra' ? '#d4f8d4'
        : asset.signal === 'Venda' ? '#f8d4d4' : '#f0f0f0';

    document.getElementById(`updated-${asset.ticker}`).textContent =
        `Atualizado em: ${new Date().toLocaleTimeString()}`;
}

// Cria e atualiza gráficos com Chart.js
function renderChart(asset) {
    const ctx = document.getElementById(`chart-${asset.ticker}`).getContext('2d');

    const candles = asset.candles.map(c => ({
        x: new Date(c.time),
        o: c.open,
        h: c.high,
        l: c.low,
        c: c.close
    }));

    const vwapData = asset.vwapData.map(v => ({ x: new Date(v.time), y: v.value }));
    const upperData = asset.upperBand.map(v => ({ x: new Date(v.time), y: v.value }));
    const lowerData = asset.lowerBand.map(v => ({ x: new Date(v.time), y: v.value }));

    const signals = asset.signals.map(s => ({
        x: new Date(s.time),
        y: s.price,
        type: s.type // 'Compra' ou 'Venda'
    }));

    if (ctx.chartInstance) ctx.chartInstance.destroy();

    ctx.chartInstance = new Chart(ctx, {
        type: 'candlestick',
        data: {
            datasets: [
                {
                    label: 'Candles',
                    data: candles
                },
                {
                    label: 'VWAP',
                    data: vwapData,
                    borderColor: 'blue',
                    borderWidth: 1,
                    fill: false,
                    pointRadius: 0
                },
                {
                    label: 'Upper Band',
                    data: upperData,
                    borderColor: 'rgba(0,0,255,0.2)',
                    fill: '+1',
                    pointRadius: 0
                },
                {
                    label: 'Lower Band',
                    data: lowerData,
                    borderColor: 'rgba(0,0,255,0.2)',
                    fill: '-1',
                    pointRadius: 0
                },
                {
                    label: 'Sinais',
                    data: signals.map(s => ({ x: s.x, y: s.y })),
                    backgroundColor: signals.map(s => s.type === 'Compra' ? 'green' : 'red'),
                    type: 'bubble'
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { type: 'time', time: { unit: 'minute' } },
                y: { beginAtZero: false }
            }
        }
    });
}

async function updateDashboard() {
    const data = await fetchData();

    for (const asset of data) {
        if (!document.getElementById(`card-${asset.ticker}`)) createCard(asset);
        updateCard(asset);
        renderChart(asset);
    }
}

updateDashboard();
setInterval(updateDashboard, updateInterval);
