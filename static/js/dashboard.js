async function fetchData(){
const res = await fetch('/api/data');
if(!res.ok) throw new Error('Falha ao buscar /api/data');
return await res.json();
}


function buildCard(symbol, data){
const card = document.createElement('div');
card.className = 'card';
const title = document.createElement('h2');
title.textContent = symbol;
card.appendChild(title);


const meta = document.createElement('div');
meta.className = 'meta';
if(data.error){
meta.innerHTML = `<strong>Erro:</strong> ${data.error}`;
card.appendChild(meta);
return card;
}


meta.innerHTML = `<div>Último preço: ${data.last_price ?? '—'}</div><div>Sinal: ${data.signal}</div>`;
card.appendChild(meta);


// color
if(data.signal === 'BUY') card.classList.add('green');
else if(data.signal === 'SELL') card.classList.add('red');
else card.classList.add('hold');


// plot container
const plotdiv = document.createElement('div');
plotdiv.className = 'plot';
card.appendChild(plotdiv);


// if candles
if(Array.isArray(data.candles) && data.candles.length){
const times = data.candles.map(c=>c.datetime);
const opens = data.candles.map(c=>c.open);
const highs = data.candles.map(c=>c.high);
const lows = data.candles.map(c=>c.low);
