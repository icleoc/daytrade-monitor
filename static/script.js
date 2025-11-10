async function loadVWAP() {
  try {
    const response = await fetch("/vwap");
    const data = await response.json();

    const container = document.getElementById("cards");
    container.innerHTML = "";

    Object.keys(data).forEach(symbol => {
      const asset = data[symbol];
      const card = document.createElement("div");
      card.className = "card";

      let signalClass = "";
      if (asset.signal.includes("Compra")) signalClass = "buy";
      else if (asset.signal.includes("Venda")) signalClass = "sell";
      else signalClass = "neutral";

      card.innerHTML = `
        <h2>${symbol}</h2>
        <p><strong>Preço:</strong> ${asset.price ? asset.price.toFixed(4) : "Sem dados"}</p>
        <p><strong>VWAP:</strong> ${asset.vwap ? asset.vwap.toFixed(4) : "Sem dados"}</p>
        <p class="signal ${signalClass}">${asset.signal}</p>
        <p class="time">Atualizado em: ${new Date(asset.timestamp).toLocaleTimeString()}</p>
      `;
      container.appendChild(card);
    });
  } catch (error) {
    console.error("Erro ao carregar dados VWAP:", error);
  }
}

loadVWAP();
setInterval(loadVWAP, 30000);
