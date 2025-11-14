const main = document.getElementById('cards');
chartEl.innerHTML = '<div class="err">Sem dados</div>';
card.style.backgroundColor = '#f2f2f2';
return;
}


statusEl.textContent = data.signal || 'HOLD';
priceEl.textContent = `Último preço: ${data.last}`;
// color card
if (data.signal === 'BUY') card.style.backgroundColor = '#e6ffed';
else if (data.signal === 'SELL') card.style.backgroundColor = '#ffe6e6';
else card.style.backgroundColor = 'white';


// build plotly candlestick
const candles = data.candles.map(c => ({
t: new Date(c.t), o: c.o, h: c.h, l: c.l, c: c.c
}));
const times = candles.map(c => c.t);
const traceCandle = {
x: times,
open: candles.map(c=>c.o),
high: candles.map(c=>c.h),
low: candles.map(c=>c.l),
close: candles.map(c=>c.c),
type: 'candlestick',
name: 'Price'
};
const vwap = data.bands.map(b => b.vwap);
const upper = data.bands.map(b => b.upper);
const lower = data.bands.map(b => b.lower);
const traceVwap = { x: times, y: vwap, type: 'scatter', mode: 'lines', name: 'VWAP' };
const traceUpper = { x: times, y: upper, type: 'scatter', mode: 'lines', name: 'Upper' };
const traceLower = { x: times, y: lower, type: 'scatter', mode: 'lines', name: 'Lower' };


const annotations = [];
// mark last signal on chart
if (data.signal && data.signal !== 'HOLD') {
const lastIdx = times.length - 1;
annotations.push({
x: times[lastIdx], y: candles[lastIdx].c,
xref: 'x', yref: 'y', showarrow: true,
arrowhead: 2,
ax: 0, ay: data.signal === 'BUY' ? 30 : -30,
text: data.signal === 'BUY' ? 'COMPRA' : 'VENDA',
font: {color: '#000'}
});
}


const layout = { margin: {t:20}, annotations };
Plotly.newPlot(chartEl, [traceCandle, traceVwap, traceUpper, traceLower], layout, {responsive:true});
}


async function refresh(){
try{
const res = await fetch('/api/data');
if(!res.ok) throw new Error(await res.text());
const j = await res.json();
for(const sym of SYMBOLS){
createOrUpdateCard(sym, j[sym] || {error: 'Sem dados'});
}
}catch(err){
console.error('Fetch error', err);
}
}


// Initial
refresh();
setInterval(refresh, UPDATE_INTERVAL);
