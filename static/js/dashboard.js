async function fetchData() {
  try {
    const res = await fetch("/api/data");
    if (!res.ok) throw new Error("Erro ao obter /api/data");
    const j = await res.json();
    return j;
  } catch (e) {
    console.error(e);
    return { error: e.message };
  }
}

function createCard(symbol) {
  const card = document.createElement("div");
  card.className = "card";
  card.id = `card-${symbol}`;

  const title = document.createElement("h2");
  title.innerText = symbol;
  card.appendChild(title);

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.innerHTML = `<span class="small">Último preço: <span id="price-${symbol}">—</span></span>`;
  card.appendChild(meta);

  const sig = document.createElement("div");
  sig.className = "signal HOLD";
  sig.id = `signal-${symbol}`;
  sig.innerText = "HOLD";
  card.appendChild(sig);

  const canvasBox = document.createElement("div");
  canvasBox.className = "canvas-placeholder";
  canvasBox.id = `chart-${symbol}`;
  canvasBox.innerText = "Gráfico (candles + VWAP)";
  card.appendChild(canvasBox);

  return card;
}

function renderEmptyCards(symbols) {
  const container = document.getElementById("cards");
  container.innerHTML = "";
  symbols.forEach(s => container.appendChild(createCard(s)));
}

function colorCardBySignal(symbol, signal) {
  const card = document.getElementById(`card-${symbol}`);
  if (!card) return;
  card.style.border = "1px solid rgba(255,255,255,0.04)";
  if (signal === "BUY") {
    card.style.boxShadow = "0 6px 18px rgba(40,167,69,0.08)";
  } else if (signal === "SELL") {
    card.style.boxShadow = "0 6px 18px rgba(220,53,69,0.08)";
  } else {
    card.style.boxShadow = "none";
  }
}

function updateCard(symbol, obj) {
  const priceEl = document.getElementById(`price-${symbol}`);
  const sigEl = document.getElementById(`signal-${symbol}`);
  if (obj.error) {
    priceEl.innerText = `Erro: ${obj.error}`;
    sigEl.innerText = "ERROR";
    sigEl.className = "signal HOLD";
    colorCardBySignal(symbol, "HOLD");
    return;
  }
  priceEl.innerText = obj.last_close ?? "—";
  sigEl.innerText = obj.signal ?? "HOLD";
  sigEl.className = `signal ${obj.signal ?? "HOLD"}`;
  colorCardBySignal(symbol, obj.signal ?? "HOLD");

  // chart placeholder: for now we show min/max/last of returned candles
  const chartBox = document.getElementById(`chart-${symbol}`);
  if (obj.candles && obj.candles.length) {
    const last = obj.candles[obj.candles.length - 1];
    const min = Math.min(...obj.candles.map(c => c.low));
    const max = Math.max(...obj.candles.map(c => c.high));
    chartBox.innerHTML = `Último: ${last.close} — Min: ${min} — Max: ${max}`;
  } else {
    chartBox.innerText = "Sem candles disponíveis";
  }
}

async function loop() {
  document.getElementById("status").innerText = "Atualizando...";
  const data = await fetchData();
  if (data.error) {
    document.getElementById("status").innerText = "Erro: " + data.error;
    return;
  }
  SYMBOLS.forEach(sym => {
    const obj = data[sym] || { error: "Sem dados" };
    updateCard(sym, obj);
  });
  document.getElementById("status").innerText = "Última atualização: " + new Date().toLocaleString();
}

window.addEventListener("load", () => {
  renderEmptyCards(SYMBOLS);
  loop();
  setInterval(loop, UPDATE_INTERVAL * 1000);
});
