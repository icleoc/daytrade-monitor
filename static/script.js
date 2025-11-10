// static/script.js
async function fetchVWAP() {
  try {
    const res = await fetch('/api/vwap');
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    const data = await res.json();
    renderCards(data);
  } catch (err) {
    document.getElementById('status').innerText = 'Erro ao buscar dados: ' + err.message;
  }
}

function renderCards(data) {
  const container = document.getElementById('cards');
  container.innerHTML = '';
  for (const key of Object.keys(data)) {
    const item = data[key];
    const card = document.createElement('div');
    card.className = 'card';
    let content = `<h2>${key}</h2>`;
    if (item.vwap !== undefined && item.vwap !== null) {
      content += `<div class="value">${item.vwap}</div>`;
    } else if (item.error) {
      content += `<div class="error">Error: ${item.error}</div>`;
    } else if (item.warning) {
      content += `<div class="warning">${item.warning}</div><div class="value">${item.vwap}</div>`;
    } else {
      content += `<div class="error">Sem dados</div>`;
    }
    card.innerHTML = content;
    container.appendChild(card);
  }
}

fetchVWAP();
setInterval(fetchVWAP, 5000);
