// dashboard.js
(async function(){
  function el(tag, cls){ const d = document.createElement(tag); if(cls) d.className = cls; return d; }

  const container = document.getElementById("cards-container");

  function createCard(symbol){
    const card = el("div","card card-hold");
    card.id = `card-${symbol}`;

    const header = el("div","card-header");
    const title = el("div","card-title"); title.textContent = symbol;
    const badge = el("div","signal-badge"); badge.textContent = "—";
    header.appendChild(title);
    header.appendChild(badge);

    const body = el("div","card-body");
    const priceRow = el("div","price-row");
    const priceMain = el("div","price-main"); priceMain.textContent = "Último preço: —";
    const stat = el("div","stat-line"); stat.textContent = "";
    priceRow.appendChild(priceMain);
    priceRow.appendChild(stat);

    const chartDiv = el("div","chart");
    chartDiv.id = `chart-${symbol}`;

    body.appendChild(priceRow);
    body.appendChild(chartDiv);

    card.appendChild(header);
    card.appendChild(body);
    container.appendChild(card);

    return { card, badge, priceMain, stat, chartDiv };
  }

  // create cards for each symbol
  const cards = {};
  SYMBOLS.forEach(s => {
    cards[s] = createCard(s);
  });

  // helper to color card
  function setCardSignal(symbol, signal){
    const cardEl = document.getElementById(`card-${symbol}`);
    const badge = cardEl.querySelector(".signal-badge");
    cardEl.classList.remove("card-buy","card-sell","card-hold");
    if(signal === "BUY"){
      cardEl.classList.add("card-buy");
      badge.style.background = getComputedStyle(document.documentElement).getPropertyValue('--green');
      badge.textContent = "COMPRA";
    }else if(signal === "SELL"){
      cardEl.classList.add("card-sell");
      badge.style.background = getComputedStyle(document.documentElement).getPropertyValue('--red');
      badge.textContent = "VENDA";
    }else{
      cardEl.classList.add("card-hold");
      badge.style.background = getComputedStyle(document.documentElement).getPropertyValue('--gray');
      badge.textContent = "HOLD";
    }
  }

  // plotly plot function
  function plotSymbol(symbol, payload){
    const containerId = `chart-${symbol}`;
    const div = document.getElementById(containerId);
    if(!payload || payload.error){
      div.innerHTML = `<div style="color:#b91c1c;padding:12px;">Erro: ${payload && payload.error ? payload.error : "Sem dados"}</div>`;
      return;
    }

    const times = payload.timestamps;
    const o = payload.open, h = payload.high, l = payload.low, c = payload.close;
    const vwap = payload.vwap, upper = payload.upper, lower = payload.lower;
    const signals = payload.signals || [];

    const traceCandles = {
      x: times,
      open: o, high: h, low: l, close: c,
      type: 'candlestick',
      name: symbol,
      increasing: {line: {color: '#0f9d58'}},
      decreasing: {line: {color: '#d33b3b'}}
    };

    const traceVWAP = {
      x: times,
      y: vwap,
      mode: 'lines',
      name: 'VWAP',
      line: {width: 2, dash: 'solid'}
    };

    const traceUpper = { x: times, y: upper, mode:'lines', name: 'Upper', showlegend:false, line:{width:1, dash:'dash'} };
    const traceLower = { x: times, y: lower, mode:'lines', name: 'Lower', showlegend:false, line:{width:1, dash:'dash'} };

    const layout = {
      margin: {t:20, r:10, l:40, b:30},
      xaxis: {rangeslider: {visible: false}},
      yaxis: {fixedrange: false},
      hovermode: 'x unified',
      showlegend: true
    };

    const data = [traceCandles, traceVWAP, traceUpper, traceLower];

    // annotations for signals (COMPRA under candle, VENDA over candle)
    const annotations = [];
    signals.forEach(s => {
      annotations.push({
        x: s.time,
        y: s.price,
        xref: 'x',
        yref: 'y',
        text: s.type === 'BUY' ? 'COMPRA' : 'VENDA',
        showarrow: true,
        arrowhead: 1,
        ay: s.type === 'BUY' ? 20 : -20,
        arrowcolor: s.type === 'BUY' ? 'green' : 'red',
        font: {color: s.type === 'BUY' ? 'green' : 'red', size:12}
      });
    });

    layout.annotations = annotations;

    Plotly.newPlot(div, data, layout, {responsive:true});
  }

  // fetch and update
  async function fetchAndUpdate(){
    try{
      const resp = await fetch("/api/data");
      const json = await resp.json();
      for(const s of SYMBOLS){
        const payload = json[s];
        // update price and stats
        const cardObj = cards[s];
        if(!payload){
          cardObj.priceMain.textContent = "Último preço: —";
          cardObj.stat.textContent = "Sem dados";
          plotSymbol(s, {error: "Sem dados"});
          continue;
        }
        if(payload.error){
          cardObj.priceMain.textContent = `Último preço: Erro: ${payload.error}`;
          cardObj.stat.textContent = "ERROR";
          setCardSignal(s, "HOLD");
          plotSymbol(s, payload);
          continue;
        }
        const lastPrice = payload.close[payload.close.length -1];
        cardObj.priceMain.textContent = `Último preço: ${lastPrice}`;
        const summary = payload.summary || {};
        const lastSignal = summary.last_signal || "HOLD";
        setCardSignal(s, lastSignal);
        // small stat: last/min/max
        let minv = Math.min(...payload.low), maxv = Math.max(...payload.high);
        cardObj.stat.textContent = `Último: ${lastPrice} — Min: ${minv} — Max: ${maxv}`;
        // plot
        plotSymbol(s, payload);
      }
    }catch(err){
      console.error("Erro fetchAndUpdate:", err);
    } finally {
      // agendamos nova atualização
      setTimeout(fetchAndUpdate, UPDATE_INTERVAL*1000);
    }
  }

  // iniciar
  fetchAndUpdate();

})();
