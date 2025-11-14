async function fetchData() {
    const res = await fetch("/api/data");
    return await res.json();
}

function createCard(symbol) {
    const tpl = document.getElementById("card-template");
    const card = tpl.content.cloneNode(true);
    card.querySelector(".sym").textContent = symbol;
    return card;
}

function getLastSignal(df) {
    const signals = df.signal;
    for (let i = signals.length - 1; i >= 0; i--) {
        if (signals[i] === "buy" || signals[i] === "sell") {
            return signals[i];
        }
    }
    return "none";
}

function renderChart(container, df) {
    const time = df.time;
    const open = df.open;
    const high = df.high;
    const low = df.low;
    const close = df.close;
    const vwap = df.vwap;
    const upper = df.upper;
    const lower = df.lower;

    // Buy / Sell markers
    const buy_x = [];
    const buy_y = [];
    const sell_x = [];
    const sell_y = [];

    df.signal.forEach((sig, i) => {
        if (sig === "buy") {
            buy_x.push(time[i]);
            buy_y.push(low[i] * 0.998);
        }
        if (sig === "sell") {
            sell_x.push(time[i]);
            sell_y.push(high[i] * 1.002);
        }
    });

    const candleTrace = {
        x: time,
        open,
        high,
        low,
        close,
        type: "candlestick",
        name: "Candles",
    };

    const vwapTrace = {
        x: time,
        y: vwap,
        mode: "lines",
        name: "VWAP",
        line: { width: 2 }
    };

    const upperTrace = {
        x: time,
        y: upper,
        mode: "lines",
        name: "Upper",
        line: { dash: "dot" }
    };

    const lowerTrace = {
        x: time,
        y: lower,
        mode: "lines",
        name: "Lower",
        line: { dash: "dot" }
    };

    const buyTrace = {
        x: buy_x,
        y: buy_y,
        mode: "markers+text",
        name: "BUY",
        text: "COMPRA",
        textposition: "bottom center",
        marker: { size: 14, color: "green" }
    };

    const sellTrace = {
        x: sell_x,
        y: sell_y,
        mode: "markers+text",
        name: "SELL",
        text: "VENDA",
        textposition: "top center",
        marker: { size: 14, color: "red" }
    };

    Plotly.newPlot(
        container,
        [candleTrace, vwapTrace, upperTrace, lowerTrace, buyTrace, sellTrace],
        {
            margin: { t: 20, b: 30 },
            showlegend: true
        }
    );
}

async function updateDashboard() {
    const data = await fetchData();

    const cardsDiv = document.getElementById("cards");
    cardsDiv.innerHTML = ""; // reset

    SYMBOLS.forEach(symbol => {
        const df = data[symbol];
        if (!df) return;

        const card = createCard(symbol);
        const el = card.querySelector(".card");

        // STATUS SIGNAL
        const lastSignal = getLastSignal(df);
        const status = card.querySelector(".status");

        if (lastSignal === "buy") {
            status.textContent = "COMPRA";
            el.style.borderColor = "green";
        } else if (lastSignal === "sell") {
            status.textContent = "VENDA";
            el.style.borderColor = "red";
        } else {
            status.textContent = "NEUTRO";
            el.style.borderColor = "#999";
        }

        // PRICE
        const price = df.close[df.close.length - 1];
        card.querySelector(".price").textContent =
            "Último preço: " + price.toFixed(5);

        // CHART
        const chartDiv = card.querySelector(".chart");
        renderChart(chartDiv, df);

        cardsDiv.appendChild(card);
    });
}

// Start
updateDashboard();
setInterval(updateDashboard, UPDATE_INTERVAL);
