async function fetchData() {
  const res = await fetch("/api/data");
  return await res.json();
}

function createCard(symbol) {
  const div = document.createElement("div");
  div.className = "card hold";
  div.id = `card-${symbol}`;
  div.innerHTML = `
    <h2>${symbol}</h2>
    <p id="price-${symbol}">Carregando...</p>
    <canvas id="chart-${symbol}"></canvas>
  `;
  document.getElementById("dashboard").appendChild(div);
}

function updateCard(symbol, info) {
  const card = document.getElementById(`card-${symbol}`);
  if (!card || !info) return;

  const priceEl = document.getElementById(`price-${symbol}`);
  if (info.error) {
    priceEl.innerText = `Erro: ${info.error}`;
    card.className = "card hold";
    return;
  }

  priceEl.innerText = `Preço: $${info.price.toFixed(2)} | Sinal: ${info.signal}`;
  card.className = `card ${info.signal.toLowerCase()}`;
  renderChart(symbol, info.data);
}

function renderChart(symbol, data) {
  if (!data || data.length === 0) return;

  const ctx = document.getElementById(`chart-${symbol}`).getContext("2d");
  const labels = data.map(d => d.datetime);
  const close = data.map(d => parseFloat(d.close));
  const vwap = data.map(d => parseFloat(d.vwap));
  const upper = data.map(d => parseFloat(d.upper_band));
  const lower = data.map(d => parseFloat(d.lower_band));

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Preço", data: close, borderColor: "#fff", fill: false },
        { label: "VWAP", data: vwap, borderColor: "#ffcc00", fill: false },
        { label: "Upper", data: upper, borderColor: "#00c853", borderDash: [5,5], fill: false },
        { label: "Lower", data: lower, borderColor: "#d32f2f", borderDash: [5,5], fill: false },
      ]
    },
    options: {
      plugins: { legend: { labels: { color: '#f5f5f5' } } },
      scales: {
        x: { ticks: { color: '#ccc' }, grid: { color: '#333' } },
        y: { ticks: { color: '#ccc' }, grid: { color: '#333' } }
      }
    }
  });
}

async function refresh() {
  const data = await fetchData();
  for (const item of data) {
    updateCard(item.symbol, item);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  SYMBOLS.forEach(createCard);
  refresh();
  setInterval(refresh, 60000); // atualiza a cada 1 min
});
