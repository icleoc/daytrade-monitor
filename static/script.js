async function fetchData() {
    const res = await fetch('/api/data');
    const assets = await res.json();
    renderDashboard(assets);
}

function renderDashboard(assets) {
    const container = document.getElementById('dashboard');
    container.innerHTML = '';

    assets.forEach(asset => {
        const card = document.createElement('div');
        card.className = 'asset-card';
        card.style.border = asset.signal === 'Compra' ? '2px solid green' : asset.signal === 'Venda' ? '2px solid red' : '1px solid #ccc';

        const title = document.createElement('h2');
        title.textContent = `${asset.ticker} - Preço: ${asset.price}`;
        card.appendChild(title);

        const canvas = document.createElement('canvas');
        card.appendChild(canvas);

        container.appendChild(card);

        new Chart(canvas.getContext('2d'), {
            type: 'candlestick',
            data: {
                datasets: [
                    { label: 'Candles', data: asset.candles },
                    { label: 'VWAP', type: 'line', data: asset.vwapData, borderColor: 'blue', borderWidth: 1, fill: false },
                    { label: 'Upper Band', type: 'line', data: asset.upperBand, borderColor: 'rgba(0,0,255,0.2)', fill: '+1' },
                    { label: 'Lower Band', type: 'line', data: asset.lowerBand, borderColor: 'rgba(0,0,255,0.2)', fill: '-1' },
                    { label: 'Sinais', type: 'scatter', data: asset.signals.map(s => ({x:s.time, y:s.price})), backgroundColor: asset.signals.map(s => s.type==='Compra'?'green':'red') }
                ]
            },
            options: {
                plugins: { legend: { display: true } },
                scales: { x: { type: 'time', time: { unit: 'minute' } } }
            }
        });
    });
}

// Atualiza a cada 15s
fetchData();
setInterval(fetchData, 15000);
