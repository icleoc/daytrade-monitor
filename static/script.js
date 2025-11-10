const cardsRoot = document.getElementById('cards');


function renderSignals(signals) {
cardsRoot.innerHTML = '';
for (const name of Object.keys(signals)) {
const s = signals[name];
const card = document.createElement('div');
card.className = 'card';


const title = document.createElement('h2');
title.textContent = name;
card.appendChild(title);


const price = document.createElement('p');
price.innerHTML = `<strong>Preço:</strong> ${s.preco === null ? '-' : s.preco}`;
card.appendChild(price);


const vwap = document.createElement('p');
vwap.innerHTML = `<strong>VWAP:</strong> ${s.vwap === null ? '-' : s.vwap}`;
card.appendChild(vwap);


const sinal = document.createElement('p');
sinal.innerHTML = `<strong>Sinal:</strong> <span class="signal ${s.sinal}">${s.sinal}</span>`;
card.appendChild(sinal);


cardsRoot.appendChild(c
