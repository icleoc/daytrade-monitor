// static/script.js
async function loadVWAP(){
  try {
    const res = await fetch('/api/vwap');
    const j = await res.json();
    const assets = j.assets;
    const container = document.getElementById('cards');
    container.innerHTML = '';
    assets.forEach(a => {
      let html;
      if(a.error) {
        html = `<div class="card"><h2>${a.symbol}</h2><p>Error: ${a.error}</p></div>`;
      } else {
        html = `<div class="card">
                  <h2>${a.symbol}</h2>
                  <p><strong>Preço:</strong> ${a.price}</p>
                  <p><strong>VWAP:</strong> ${a.vwap}</p>
                  <p><strong>Sinal:</strong> ${a.signal}</p>
                  <p><small>TF: ${a.timeframe}</small></p>
                </div>`;
      }
      container.innerHTML += html;
    });
  } catch(err) {
    console.error('Erro ao carregar dados VWAP:', err);
  }
}

window.onload = loadVWAP;
setInterval(loadVWAP, 5000);
