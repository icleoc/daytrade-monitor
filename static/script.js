async function atualizarVWAP() {
    const response = await fetch("/api/vwap");
    const data = await response.json();
    const cardsDiv = document.getElementById("cards");
    cardsDiv.innerHTML = "";

    Object.keys(data).forEach(asset => {
        const info = data[asset];
        if (info.error) {
            cardsDiv.innerHTML += `
                <div class="card">
                    <h2>${asset}</h2>
                    <p>${info.error}</p>
                </div>`;
        } else {
            cardsDiv.innerHTML += `
                <div class="card">
                    <h2>${asset}</h2>
                    <p><strong>Preço:</strong> ${info.price}</p>
                    <p><strong>VWAP:</strong> ${info.vwap}</p>
                    <p class="${info.signal.toLowerCase()}"><strong>Sinal:</strong> ${info.signal}</p>
                </div>`;
        }
    });
}

setInterval(atualizarVWAP, 5000);
window.onload = atualizarVWAP;
