const INTERVAL_SEC = 30; // default update


async function fetchJson(url){
const res = await fetch(url);
if(!res.ok) throw new Error(`${res.status} ${res.statusText}`);
return res.json();
}


function buildCardDom(key, data){
const card = document.createElement('section');
card.className = 'card ' + (data.signal && data.signal !== 'NEUTRAL' ? data.signal.toLowerCase() : 'neutral');
card.id = `card-${key}`;
card.innerHTML = `
<h2>${key} <small style="font-weight:400">(${data.ticker || ''})</small></h2>
<div class="price">Preço: <span class="price-val">${data.price ?? 'Sem dados'}</span></div>
<div class="vwap">VWAP: <span class="vwap-val">${data.vwap ?? 'Sem dados'}</span></div>
<div id="plot-${key}" class="plot"></div>
<div class="footer-note">Sinal: <strong class="signal-val">${data.signal ?? 'NO_DATA'}</strong> — Atualizado: ${data.last_update ?? ''}</div>
`;
return card;
}


async function updateDashboard(){
try{
const data = await fetchJson(`${API_BASE}/vwap`);
const container = document.getElementById('cards-container');
container.innerHTML = '';
for(const key of Object.keys(data)){
const item = data[key];
const card = buildCardDom(key, item);
container.appendChild(card);
// request chart data and plot
plotTicker(key, item.ticker);
}
}catch(e){
console.error('updateDashboard error', e);
}
}


async function plotTicker(key, ticker){
if(!ticker) return;
try{
const chart = await fetchJson(`${API_BASE}/chart/${encodeURIComponent(ticker)}?period=1d&interval=15m`);
if(chart.error) return;
const times = chart.times;
const o = chart.open, h = chart.high, l = chart.low, c = chart.close;
const vwap = chart.vwap, upper = chart.upper, lower = chart.lower;
const signal = chart.signal;
const traceCandles = {
x: times, close: c, high: h, low: l, open: o,
type: 'candlestick', name: 'Candles'
};
const traceVWAP = { x: times, y: vwap, type: 'scatter', mode: 'lines', name: 'VWAP', line: {width:2} };
const traceUpper = { x: times, y: upper, type: 'scatter', mode: 'lines', name: 'Upper', fill: 'tonexty', visible: true, line: {width:0.5} };
const traceLower = { x: times, y: lower, type: 'scatter', mode: 'lines', name: 'Lower', fill: 'tonexty', visible: true, line: {width:0.5} };


const data = [t
