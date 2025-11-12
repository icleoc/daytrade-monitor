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

            signalEl.style.color = asset.signal === 'buy' ? 'green' :
                                   asset.signal === 'sell' ? 'red' : 'gray';
        });
    } catch (e) {
        console.error("Erro ao carregar dados:", e);
    }
}

setInterval(loadData, 10000);
loadData();
