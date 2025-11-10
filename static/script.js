// static/script.js
async function loadVWAP(){
  try{
    const res = await fetch('/api/vwap');
    const j = await res.json();
    const container = document.getElementById('cards');
    container.innerHTML = '';
    j.assets.forEach(a => {
      const card = document.createElement('div');
      card.className = 'card';
      if(a.error){
        card.innerHTML = `<h3>${a.symbol}</h3><p class="error">${a.error}</p>`;
      } else {
        card.innerHTML = `<h3>${a.symbol}</h3>
          <p>${a.price !== null ? a.price.toFixed(4) : '-'}</p>
          <small>VWAP: ${a.vwap !== null ? a.vwap.toFixed(4) : '-'}</small>
          <p>Sinal: <b>${a.signal}</b></p>
          <small>${a.timeframe}</small>`;
      }
      container.appendChild(card);
    });
  }catch(err){
    console.error(err);
  }
}

setInterval(loadVWAP, 5000);
window.onload = loadVWAP;
